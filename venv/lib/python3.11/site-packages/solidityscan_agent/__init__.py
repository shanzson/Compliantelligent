import click

from solidityscan_agent.config import Config
from solidityscan_agent.report import Report
from solidityscan_agent.scan import Scan

"""
    each command is mapped to @config.command()
    commands can be grouped. a group can be created by mapping the method to @config.group()
"""

# base group. under which all other subcommands go.
@click.group()
def solidityscan():
    pass

# config command, with subcommands.
@solidityscan.group()
def config():
    """config file actions"""
    pass

# adds config to the default config path
@config.command()
@click.option("--token", prompt=False, required=False, type=str, help="api token generated from solidityscan")
@click.option("--error-language", prompt=False, required=False, type=str, help="language code for error messages. defaults to 'en'")
def add_update_config(token, error_language):
    """edit config file"""
    if not token and not error_language:
        raise click.UsageError("--token or --error-language is required")

    Config.add_update_config(token, error_language)

# shows the config path
# todo: make config path editable
@config.command()
def show_config_path():
    """show default config path"""
    Config.get_config_path()

# does a scan
@solidityscan.command()
@click.option("--scan-type", "-s", required=True, type=click.Choice(["project", "contract"]), prompt=False, help="type of scan to perform")
@click.option("-project-url", required=False, help="project url to scan")
@click.option("-project-branch", required=False, help="branch of the project")
@click.option("-skip-file-paths", required=False, help="file paths to skip scanning", multiple=True)
@click.option("-rescan", "-r", is_flag=True, required=False, help="flag to denote if the scan is a rescan")
@click.option("-contract-address", required=False, help="address of the contract")
@click.option("-contract-chain", required=False, help="chain of the contract")
@click.option("-contract-platform", required=False, help="platform of the contract")
@click.option("--token", "-t", required=False, help="api token generated from solidityscan")
def scan(scan_type, project_url, project_branch, skip_file_paths, rescan, contract_address, contract_chain, contract_platform, token):
    """perform scans on blocks or projects"""
    
    """
        takes input parameters via CLI and does a scan.
        2 allowed scan_types -> project, block

        if there is a --token parameter, the token will not be picked up from config file.
        if there is a -r or -rescan flag, the scan will be considered a rescan
    """

    s = Scan()

    if scan_type == "project":
        if not project_url:
            raise click.UsageError("-project-url flag is required")
        if not project_branch:
            raise click.UsageError("-project-branch flag is required")

        s.project_scan(project_url, project_branch, rescan, skip_file_paths, token)
    elif scan_type == "contract":
        if not contract_address:
            raise click.UsageError("-contract-address flag is required")
        if not contract_chain:
            raise click.UsageError("-contract-chain flag is required")
        if not contract_platform:
            raise click.UsageError("-contract-platform flag is required")
        
        s.block_scan(contract_address, contract_chain, contract_platform, rescan, token)

@solidityscan.command()
@click.option("--report-type", "-r", required=True, type=click.Choice(["generate"]), prompt=False, help="report command")
@click.option("-project-id", required=False, help="project id to generate report for")
@click.option("-scan-id", required=False, help="scan associated with the project")
def report(report_type, project_id, scan_id):
    """perform report related actions"""

    r = Report()

    if report_type == "generate":
        if not project_id:
            raise click.UsageError("-project-id flag is required")
        if not scan_id:
            raise click.UsageError("-scan-id flag is required")

        r.generate_report(project_id, scan_id)

if __name__ == "__main__":
    solidityscan()
