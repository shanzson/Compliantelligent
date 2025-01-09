from solidityscan_agent.config import Config

import requests
import click

from solidityscan_agent.exceptions import ReportGenerationFailed, ScanFailed, HostNotReachable
from solidityscan_agent.constants import HOST

class Report:

    @property
    def generate_report_url(self):
        return f"{HOST}/api-generate-report/"

    def make_headers(self, token):
        return {
            "Authorization": f"Bearer {token}"
        }

    def generate_report(self, project_id, scan_id, token=None):
        try:
            if not token:
                token = Config.get_token_from_config()
            url = self.generate_report_url
            headers = self.make_headers(token)
            body = {
                "project_id": project_id,
                "scan_id": scan_id,
            }
            response = requests.post(url, json=body, headers=headers)
            json_response = response.json()

            if response.status_code // 100 == 2:
                click.echo(json_response)
            else:
                # if the report_generation fails for some reason
                raise ReportGenerationFailed(json_response)
        except Exception as e:
            raise HostNotReachable()
