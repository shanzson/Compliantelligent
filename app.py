import os
import zipfile
import json
import requests  # Add this import
from flask import Flask, request, jsonify, render_template, stream_with_context, Response
from analyzer.smart_contract_analyzer import SmartContractAnalyzer
from dotenv import load_dotenv
from solidityscan_runner import SolidityScanRunner  # Update import to use the class

# Load environment variables from .env file
load_dotenv()

# Initialize API keys
api_key = os.getenv('OPENAI_API_KEY')
solidityscan_token = os.getenv('SOLIDITYSCAN_TOKEN')

class SolidityScanAPI:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('SOLIDITYSCAN_TOKEN', '')
        if not self.token:
            raise ValueError("SolidityScan token is required")
            
        # Debug print token info
        token_preview = f"{self.token[:10]}...{self.token[-10:]}" if len(self.token) > 20 else "..."
        print("\nDebug: Token Information")
        print("-----------------------")
        print(f"Token length: {len(self.token)}")
        print(f"Token preview: {token_preview}")
        
        # Set up headers
        self.base_url = 'https://api.solidityscan.com/private'
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, url: str, data: dict, retry_with_rescan: bool = True) -> dict:
        print(f"\nDebug: Making request to {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=600)
            response_data = response.json() if response.text else {}
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {json.dumps(response_data, indent=2)}")

            # Handle duplicate project case
            if (response.status_code == 403 and 
                response_data.get("status") == "failed" and 
                response_data.get("type") == "duplicate_project" and 
                retry_with_rescan):
                
                print("\nDuplicate project detected, retrying with rescan=true")
                data["rescan"] = True
                return self._make_request(url, data, retry_with_rescan=False)
            
            # If it's a duplicate project response, return it as success
            if (response_data.get("status") == "failed" and 
                response_data.get("type") == "duplicate_project"):
                response_data["status"] = "success"  # Convert to success
                return response_data

            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": response_data.get("message", "Request failed"),
                    "error_type": response_data.get("type", "unknown"),
                    "details": response_data
                }

            return response_data

        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }

    def scan_project(self, project_url: str, project_branch: str = "main", 
                    skip_file_paths: list = None, provider: str = "github", 
                    project_name: str = None) -> dict:
        """Start a project scan."""
        try:
            url = f"{self.base_url}/api-project-scan/"
            data = {
                "provider": provider,
                "project_name": project_name or "SolidityScan",
                "project_url": project_url,
                "project_branch": project_branch,
                "project_skip_files": skip_file_paths or [],
                "rescan": False  # Initially set to False
            }

            return self._make_request(url, data)
            
        except Exception as e:
            print(f"\nError in scan_project: {str(e)}")
            return {
                "status": "error",
                "message": f"Scan failed: {str(e)}",
                "error_type": type(e).__name__
            }

# Initialize Flask app
app = Flask(__name__)

# Initialize SolidityScan client
scanner = SolidityScanAPI(solidityscan_token)

# Home route to serve the main page
@app.route('/')
def home():
    return render_template('index.html')

# Analyze route to process the uploaded ZIP file
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'zipFile' not in request.files:
            return jsonify({'error': 'No file uploaded. Please upload a ZIP file.'}), 400

        zip_file = request.files['zipFile']
        if not zip_file.filename.endswith('.zip'):
            return jsonify({'error': 'Invalid file format. Please upload a ZIP file.'}), 400

        eips = request.form.get('eips')
        if not eips:
            return jsonify({'error': 'No EIPs selected. Please select at least one EIP.'}), 400

        eips = json.loads(eips)
        if not isinstance(eips, list) or not eips:
            return jsonify({'error': 'Invalid EIPs format. Please select valid EIPs.'}), 400

        solidity_files = extract_solidity_files(zip_file)
        if not solidity_files:
            return jsonify({'error': 'No Solidity (.sol) files found in the uploaded ZIP.'}), 400

        analyzer = SmartContractAnalyzer(api_key=api_key)
        analysis_results = {}
        
        for filename, code in solidity_files.items():
            try:
                result = analyzer.analyze_contract(contract_code=code, selected_eips=eips)
                analysis_results[filename] = {
                    'oz_modules': result.get('oz_modules', 'Unable to parse imports'),
                    'compliance': result.get('compliance', {}),
                }
            except Exception as e:
                analysis_results[filename] = {'error': f'Error analyzing file: {str(e)}'}

        return jsonify({
            'message': 'Analysis completed successfully!',
            'data': analysis_results
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/solidityscan', methods=['POST'])
def solidityscan():
    """
    Perform SolidityScan analysis using the API.
    """
    try:
        # Get parameters from request
        project_url = request.form.get('project_url')
        project_branch = request.form.get('project_branch', 'main')
        provider = request.form.get('provider', 'github')
        project_name = request.form.get('project_name')
        skip_file_paths = request.form.get('skip_file_paths', '[]')

        if not project_url:
            return jsonify({'error': 'Project URL is required.'}), 400

        # Convert skip_file_paths to list if it's a JSON string
        if isinstance(skip_file_paths, str):
            try:
                skip_file_paths = json.loads(skip_file_paths)
            except json.JSONDecodeError:
                skip_file_paths = []

        # Run the scan using the API
        results = scanner.scan_project(
            project_url=project_url,
            project_branch=project_branch,
            skip_file_paths=skip_file_paths,
            provider=provider,
            project_name=project_name
        )
        
        if results.get('status') == 'error':
            return jsonify({
                'status': 'error',
                'message': results.get('message', 'SolidityScan analysis failed'),
                'error_details': results
            }), 500
            
        # Handle successful scan, including duplicate project cases
        return jsonify({
            'status': 'success',
            'message': 'SolidityScan analysis completed successfully!',
            'results': results
        })

    except Exception as e:
        print(f"Error during SolidityScan analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def analyze_files_stream(solidity_files, eips):
    """Generator function to analyze files and stream progress."""
    analyzer = SmartContractAnalyzer(api_key)
    total_files = len(solidity_files)
    analyzed_count = 0

    yield '{"progress": [\n'

    for idx, (filename, code) in enumerate(solidity_files.items()):
        analyzed_count += 1
        try:
            print(f"Analyzing file: {filename}")
            result = analyzer.analyze_contract(contract_code=code, selected_eips=eips)
            print(f"Result for {filename}: {result}")

            progress = int((analyzed_count / total_files) * 100)
            yield json.dumps({
                "file": filename,
                "progress": progress,
                "oz_modules": result.get("oz_modules", "Unable to parse imports"),
                "compliance": result.get("compliance", {})
            })

            if idx < total_files - 1:
                yield ',\n'

        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            yield json.dumps({
                "file": filename,
                "progress": int((analyzed_count / total_files) * 100),
                "error": f"Error analyzing file: {str(e)}"
            })

    yield '\n]}'

def extract_solidity_files(zip_file):
    """Extract Solidity (.sol) files from the uploaded ZIP file."""
    try:
        solidity_files = {}
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith('.sol'):
                    with zip_ref.open(file) as f:
                        solidity_files[file] = f.read().decode('utf-8')
        return solidity_files
    except Exception as e:
        print(f"Error extracting files: {e}")
        return {}

if __name__ == '__main__':
    app.run(debug=True)