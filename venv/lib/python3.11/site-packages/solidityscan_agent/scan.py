from solidityscan_agent.config import Config

import requests
import click

from solidityscan_agent.exceptions import ScanFailed, HostNotReachable
from solidityscan_agent.constants import HOST

class Scan:

    @property
    def project_scan_host_url(self):
        return f"{HOST}/api-project-scan/"

    @property
    def block_scan_host_url(self):
        return f"{HOST}/api-start-scan-block/"

    def make_headers(self, token):
        return {
            "Authorization": f"Bearer {token}"
        }

    """
        Performs a project scan.

        project_url is required
        project_branch is required
        project_name is required
        skip_file_paths is optional
        token is optional
        rescan is optional
    """
    def project_scan(self, project_url, project_branch, rescan, skip_file_paths=[], token=None):
        try:
            if not token:
                token = Config.get_token_from_config()

            url = self.project_scan_host_url
            headers = self.make_headers(token)
            body = {
                "project_url": project_url,
                "project_branch": project_branch,
                "skip_file_paths": list(skip_file_paths),
                "rescan": rescan,
            }

            response = requests.post(url, json=body, headers=headers)
            json_response = response.json()

            if response.status_code // 100 == 2:
                click.echo(json_response)
            else:
                # if the scan fails for some reason
                raise ScanFailed(json_response)

        # if the solidityscan host is not reachable
        except requests.exceptions.RequestException as e:
            raise HostNotReachable()

    """
        Performs a block scan.

        contract_address is required
        contract_chain is required
        contract_platform is required
        rescan is optional
        token is optional
    """
    def block_scan(self, contract_address, contract_chain, contract_platform, rescan, token=None):
        try:
            if not token:
                token = Config.get_token_from_config()

            url = self.block_scan_host_url
            headers = self.make_headers(token)
            body = {
                "contract_address": contract_address,
                "contract_chain": contract_chain,
                "contract_platform": contract_platform,
                "rescan": rescan,
            }

            response = requests.post(url, json=body, headers=headers)
            json_response = response.json()

            if response.status_code // 100 == 2:
                click.echo(json_response)
            else:
                # if the scan fails for some reason
                raise ScanFailed(json_response)

        except requests.exceptions.RequestException as e:
            raise HostNotReachable()
