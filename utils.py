import json
import yaml
from jsonschema import validate


def schema_validate(json_str, schema_yml_path):
    with open(schema_yml_path) as yaml_in:
        schema = yaml.safe_load(yaml_in)
    instance = json.loads(json_str)
    return validate(
        instance=instance,
        schema=schema,
    ) is None


def get_config():
    config_file_path = sys.argv[3]
    with open(config_file_path) as cf:
        return json.load(cf)['ConnectorSpecification']
