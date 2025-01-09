import openai
from typing import List, Dict
# from solidityscan import SolidityScan


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
        Check EIP compliance based on OpenZeppelin imports and inheritance patterns.
        Logic:
        1. Check for OpenZeppelin imports
        2. Check if EIP standard contracts are imported
        3. Determine if the contract inherits from or just interacts with the EIP standard
        """
        results = {}
        
        # First check if there are any OpenZeppelin imports
        has_oz_imports = any("openzeppelin" in imp.lower() for imp in oz_imports)
        
        for eip in selected_eips:
            try:
                if not has_oz_imports:
                    results[eip] = f"❌ Does not comply with {eip}. Reason: No OpenZeppelin imports found"
                    continue

                # Check for specific EIP standard imports
                eip_import_patterns = {
                    'ERC20': '@openzeppelin/contracts/token/ERC20/ERC20.sol',
                    'ERC721': '@openzeppelin/contracts/token/ERC721/ERC721.sol',
                    'ERC1155': '@openzeppelin/contracts/token/ERC1155/ERC1155.sol'
                }
                
                # Check if this EIP's standard contract is imported
                eip_import = eip_import_patterns.get(eip, '')
                if eip_import not in str(oz_imports):
                    results[eip] = f"❌ Does not comply with {eip}. Reason: No {eip} standard contract import found"
                    continue

                # Check inheritance vs interaction
                # Look for inheritance patterns
                inheritance_patterns = {
                    'ERC20': ['contract', 'is', 'ERC20'],
                    'ERC721': ['contract', 'is', 'ERC721'],
                    'ERC1155': ['contract', 'is', 'ERC1155']
                }
                
                # Check if contract inherits from the standard
                pattern = inheritance_patterns.get(eip, [])
                is_inheriting = all(p in contract_code for p in pattern)
                
                if is_inheriting:
                    results[eip] = f"✅ Complies with {eip} (inherits OpenZeppelin's {eip})"
                else:
                    # Contract imports but doesn't inherit - means it's just using for interaction
                    results[eip] = f"❌ Does not comply with {eip}. Reason: The contract imports but does not inherit from {eip}, suggesting it only interacts with {eip} tokens"

            except Exception as e:
                results[eip] = f"❌ Error during {eip} analysis: {str(e)}"
                
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
