import os
import zipfile
import json
from flask import Flask, request, jsonify, render_template, stream_with_context, Response
from analyzer.smart_contract_analyzer import SmartContractAnalyzer  # Ensure this path is correct
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Now you can access the variables
api_key = os.getenv('OPENAI_API_KEY')


# Initialize Flask app
app = Flask(__name__)

# Home route to serve the main page
@app.route('/')
def home():
    return render_template('index.html')  # Ensure index.html exists in the templates folder

# Analyze route to process the uploaded ZIP file
@app.route('/analyze', methods=['POST'])
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Validate and retrieve the uploaded file
        if 'zipFile' not in request.files:
            return jsonify({'error': 'No file uploaded. Please upload a ZIP file.'}), 400

        zip_file = request.files['zipFile']
        if not zip_file.filename.endswith('.zip'):
            return jsonify({'error': 'Invalid file format. Please upload a ZIP file.'}), 400

        # Retrieve and parse EIPs from the form data
        eips = request.form.get('eips')
        if not eips:
            return jsonify({'error': 'No EIPs selected. Please select at least one EIP.'}), 400

        eips = json.loads(eips)
        if not isinstance(eips, list) or not eips:
            return jsonify({'error': 'Invalid EIPs format. Please select valid EIPs.'}), 400

        # Unzip the uploaded file and process Solidity files
        solidity_files = extract_solidity_files(zip_file)
        if not solidity_files:
            return jsonify({'error': 'No Solidity (.sol) files found in the uploaded ZIP.'}), 400

        # Initialize the analyzer and analyze each contract
        analyzer = SmartContractAnalyzer(api_key=api_key)
        analysis_results = {}
        total_files = len(solidity_files)
        completed_files = 0

        for filename, code in solidity_files.items():
            try:
                result = analyzer.analyze_contract(contract_code=code, selected_eips=eips)
                analysis_results[filename] = {
                    'oz_modules': result.get('oz_modules', 'Unable to parse imports'),
                    'compliance': result.get('compliance', {})
                }
                completed_files += 1
            except Exception as e:
                analysis_results[filename] = {'error': f'Error analyzing file: {str(e)}'}

            # Send real-time progress to the frontend (if needed, use WebSocket or Server-Sent Events)

        return jsonify({
            'message': 'Analysis completed successfully!',
            'progress': 100,
            'data': analysis_results
        })

    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return jsonify({'error': str(e)}), 500


def analyze_files_stream(solidity_files, eips):
    """
    Generator function to analyze files and stream progress.
    """
    analyzer = SmartContractAnalyzer(api_key)
    total_files = len(solidity_files)
    analyzed_count = 0

    yield '{"progress": [\n'  # Start of JSON response

    for idx, (filename, code) in enumerate(solidity_files.items()):
        analyzed_count += 1
        try:
            print(f"Analyzing file: {filename}")  # Debug log
            result = analyzer.analyze_contract(contract_code=code, selected_eips=eips)
            print(f"Result for {filename}: {result}")  # Debug log

            progress = int((analyzed_count / total_files) * 100)
            yield json.dumps({
                "file": filename,
                "progress": progress,
                "oz_modules": result.get("oz_modules", "Unable to parse imports"),
                "compliance": result.get("compliance", {})
            })

            if idx < total_files - 1:
                yield ',\n'  # Add a comma if not the last item

        except Exception as e:
            print(f"Error analyzing {filename}: {e}")  # Debug log
            yield json.dumps({
                "file": filename,
                "progress": int((analyzed_count / total_files) * 100),
                "error": f"Error analyzing file: {str(e)}"
            })

    yield '\n]}'  # End of JSON response


def extract_solidity_files(zip_file):
    """
    Extract Solidity (.sol) files from the uploaded ZIP file.
    """
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
