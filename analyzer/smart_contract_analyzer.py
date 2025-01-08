import openai
from typing import List, Dict
from solidityscan import SolidityScan  # Import SolidityScan SDK


class SmartContractAnalyzer:
    def __init__(self, api_key: str):
        """
        Initialize the SmartContractAnalyzer with the provided API key.
        """
        if not api_key:
            raise ValueError("API key must be provided")
        
        # Set the API key for this instance and globally for OpenAI
        self.api_key = api_key
        openai.api_key = self.api_key  # Set globally

        # Debugging: Print the API key being used
        print(f"Initializing with API key: {self.api_key}")

    def analyze_contract(self, contract_code: str, selected_eips: List[str]) -> Dict:
        """
        Analyze a single contract for OpenZeppelin imports, EIP compliance, and SolidityScan results.
        """
        # Analyze OpenZeppelin imports
        oz_imports = self.analyze_oz_imports(contract_code)

        # Check EIP compliance
        compliance = self.check_eip_compliance(contract_code, oz_imports, selected_eips)

        # Run SolidityScan analysis
        solidityscan_results = self.run_solidityscan_scan(contract_code)

        return {
            'oz_modules': oz_imports,
            'compliance': compliance,
            'solidityscan_results': solidityscan_results,
        }

    def analyze_oz_imports(self, contract_code: str) -> List[str]:
        """
        Extract OpenZeppelin imports from the smart contract code.
        """
        try:
            # Look for lines starting with "import" and containing "openzeppelin"
            import_lines = [
                line.strip()
                for line in contract_code.splitlines()
                if line.strip().startswith("import") and "openzeppelin" in line.lower()
            ]
            return import_lines if import_lines else ["No OpenZeppelin imports found."]
        except Exception as e:
            return [f"Error parsing OpenZeppelin imports: {str(e)}"]

    def check_eip_compliance(self, contract_code: str, oz_imports: List[str], selected_eips: List[str]) -> Dict:
        """
        Check if the smart contract complies with the selected EIPs using OpenAI API.
        """
        results = {}
        for eip in selected_eips:
            if eip in ['ERC20', 'ERC721', 'ERC1155']:
                try:
                    # Ask ChatGPT if the contract inherits from OpenZeppelin's base contracts
                    messages = [
                        {"role": "system", "content": "You are an AI assistant analyzing Solidity smart contracts."},
                        {
                            "role": "user",
                            "content": f"Analyze the following Solidity smart contract code. "
                                       f"Does it inherit from OpenZeppelin's {eip} base contracts "
                                       f"(e.g., ERC20, IERC20, etc.)? If it doesn't inherit, explain why.\n\n{contract_code}"
                        }
                    ]

                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=messages,
                        temperature=0
                    )

                    # Extract response from ChatGPT
                    chat_response = response['choices'][0]['message']['content'].strip()

                    if "yes" in chat_response.lower():
                        results[eip] = f"✅ Complies with this EIP (inherits OpenZeppelin's {eip})"
                    elif "no" in chat_response.lower():
                        results[eip] = f"❌ Does not comply with this EIP. Reason: {chat_response}"
                    else:
                        results[eip] = f"❌ Could not determine compliance. Response: {chat_response}"

                except Exception as e:
                    results[eip] = f"❌ Error during analysis: {str(e)}"

        return results

    def run_solidityscan_scan(self, contract_code: str) -> Dict:
        """
        Run SolidityScan analysis on the provided contract code.
        """
        try:
            scan = SolidityScan()
            results = scan.scan(scan_type="code", code=contract_code)
            return results
        except Exception as e:
            return {"error": f"SolidityScan error: {str(e)}"}

    def check_functions(self, contract_code: str, required_functions: List[str]) -> Dict:
        """
        Check for required functions and compliance with standards.
        """
        messages = [
            {"role": "system", "content": "You are an AI assistant analyzing Solidity smart contracts."},
            {"role": "user", "content": f"Analyze the following Solidity smart contract code and check if it implements the required functions {required_functions}. "
                                        f"For each function:\n- Check if it exists\n- Verify correct parameters\n- Check if it follows standard implementation.\n\n{contract_code}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )

        try:
            return eval(response.choices[0]['message']['content'].strip())
        except Exception as e:
            return {"error": f"Error parsing compliance results: {str(e)}"}

    def generate_report(self, analysis_results: Dict) -> str:
        """
        Generate a simplified report based on analysis results.
        """
        report = "Smart Contract Analysis Report\n"
        report += "===========================\n\n"

        for contract_name, data in analysis_results.items():
            report += f"{contract_name}\n"
            report += f"- OpenZeppelin Imports: {', '.join(data.get('oz_modules', ['No OpenZeppelin imports found']))}\n"
            report += "- EIP Compliance:\n"
            for eip, status in data['compliance'].items():
                report += f"  - {eip}: {status}\n"

            if "solidityscan_results" in data:
                report += "- SolidityScan Results:\n"
                for issue in data["solidityscan_results"].get("issues", []):
                    report += f"  - {issue['severity']}: {issue['description']}\n"

            report += "\n"

        return report
