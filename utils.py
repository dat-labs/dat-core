import json
import re
import yaml
from jsonschema import validate


def schema_validate(instance, schema_yml_path):
    with open(schema_yml_path) as yaml_in:
        schema = yaml.safe_load(yaml_in)
    return validate(
        instance=instance,
        schema=schema,
    ) is None

def to_snake_case(_str):
    """
    Given a camel_case string, convert it
    to snake case.
    E.g
    ThisIsCamel ---> this_is_camel
    thisIsCamel ---> this_is_camel
    """
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'_\1', _str).lower()


