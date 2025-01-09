from pathlib import Path
from ruamel.yaml import YAML
import click

from solidityscan_agent.exceptions import TokenNotFound

SOLIDITYSCAN_ENV_PATH = f"{str(Path.home())}/solidityscan.yml"

class Config:
    @staticmethod
    def load_yaml():
        try:
            with open(SOLIDITYSCAN_ENV_PATH, 'r') as f:
                yaml = YAML()
                generated = yaml.load_all(f)
                result = {}
                for x in generated:
                    result = x
                
                return result
        except IOError:
            _ = open(SOLIDITYSCAN_ENV_PATH, 'w')
            return {"version": "0.1", "token": None, "error_language": None}

    @staticmethod
    def get_config_value(key):
        return Config.load_yaml().get(key, None)

    @staticmethod
    def get_config_path():
        click.echo(SOLIDITYSCAN_ENV_PATH)

    """
        adds token field to config
        overwrites if field already contains a value
    """
    @staticmethod
    def add_update_config(token, error_language):
        yaml_data = Config.load_yaml()
        YAML_STRUCT = f"""version: {yaml_data.get('version')}"""
        if token:
            YAML_STRUCT = f"""version: 0.1\ntoken: {token}\nerror_language: {yaml_data.get('error_language')}"""
        else:
            YAML_STRUCT = f"""version: 0.1\ntoken: {yaml_data.get('token')}\nerror_language: {error_language}"""

        with open(SOLIDITYSCAN_ENV_PATH, 'w+') as f:
            f.write(YAML_STRUCT)
            
            click.echo("config file updated")

    """
        gets the token from the config file
    """
    @staticmethod
    def get_token_from_config():
        yaml_data = Config.load_yaml()

        token = yaml_data.get("token", None)
        if token is None:
            raise TokenNotFound()
        
        return token
