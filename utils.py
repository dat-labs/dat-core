import json
import yaml
from jsonschema import validate


def schema_validate(json_str, schema_yml_path, schema_key):
    with open(schema_yml_path) as yaml_in:
        schema = yaml.safe_load(yaml_in)
    instance = json.loads(json_str)
    return validate(
        instance=instance[schema_key],
        schema=schema[schema_key],
    ) is None
