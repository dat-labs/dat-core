import json
import yaml
from jsonschema import validate


def schema_validate(instance, schema_yml_path):
    with open(schema_yml_path) as yaml_in:
        schema = yaml.safe_load(yaml_in)
    return validate(
        instance=instance,
        schema=schema,
    ) is None

