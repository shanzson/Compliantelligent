import os
import time
import requests
import json
from typing import Dict, Any, Optional

class SolidityScanRunner:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('SOLIDITYSCAN_TOKEN', '')
        if not self.token:
            raise ValueError("SolidityScan token is required")
        
        # Debug print token (masked)
        token_preview = f"{self.token[:10]}...{self.token[-10:]}" if len(self.token) > 20 else "..."
        print("\nDebug: Token being used:")
        print(f"Token length: {len(self.token)}")
        print(f"Token preview: {token_preview}")
        print(f"Token starts with 'Bearer': {self.token.startswith('Bearer')}")
        
        # Ensure correct headers exactly matching the curl command
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'Authorization': f'Bearer {self.token}' if not self.token.startswith('Bearer') else self.token,
            'Content-Type': 'application/json'
        }
        
        # Debug print full Authorization header
        auth_header = self.headers['Authorization']
        auth_preview = f"{auth_header[:15]}...{auth_header[-15:]}"
        print("\nDebug: Authorization header being used:")
        print(f"Header length: {len(auth_header)}")
        print(f"Header preview: {auth_preview}")
        
        self.base_url = 'https://api.solidityscan.com/private'

    def _make_request(self, endpoint: str, data: Dict[str, Any], max_retries: int = 5, retry_delay: int = 15) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        retry_count = 0

        # Debug print request details
        print("\nDebug: Making request with:")
        print(f"URL: {url}")
        print("Headers:")
        for key, value in self.headers.items():
            if key == 'Authorization':
                print(f"{key}: {value[:15]}...{value[-15:]}")
            else:
                print(f"{key}: {value}")
        print(f"Data: {json.dumps(data, indent=2)}")

        while retry_count < max_retries:
            try:
                print(f"\nAttempt {retry_count + 1} of {max_retries}")
                
                response = requests.post(
                    url,
                    headers=self.headers,
                    data=json.dumps(data),
                    timeout=600
                )
                
                print(f"Response status code: {response.status_code}")
                print("Response headers:")
                print(response.headers)
                print("Response body:")
                print(response.text)
                
                if response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Authentication failed. Please check your token.",
                        "error_type": "AuthError",
                        "details": response.text
                    }

                response.raise_for_status()
                return {
                    "status": "success",
                    "data": response.json() if response.text else {},
                    "raw_response": response.text
                }

            except requests.exceptions.RequestException as e:
                print(f"\nRequest failed: {str(e)}")
                if retry_count < max_retries - 1:
                    print(f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                retry_count += 1

        return {
            "status": "error",
            "message": f"Request failed after {retry_count} attempts",
            "error_type": "RequestError"
        }

    def run_scan(self, project_url: str, project_branch: str = "main", 
                skip_file_paths: list = None, provider: str = "github", 
                project_name: str = None) -> Dict[str, Any]:
        data = {
            "provider": provider,
            "project_name": project_name or "SolidityScan",
            "project_url": project_url,
            "project_branch": project_branch,
            "project_skip_files": skip_file_paths or []
        }

        return self._make_request('/api-project-scan/', data)


def run_solidityscan(project_url: str, project_branch: str = "main", **kwargs) -> Dict[str, Any]:
    try:
        runner = SolidityScanRunner()
        return runner.run_scan(project_url, project_branch, **kwargs)
    except Exception as e:
        return {
            "status": "error",
            "message": f"SolidityScan analysis failed: {str(e)}",
            "error": str(e)
        }