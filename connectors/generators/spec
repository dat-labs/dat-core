#! .venv/bin/python
import json
import yaml
# from base import GeneratorsBase

def main():
    with open('./specs/ConnectorSpecification.yml') as yaml_in:
        schema = yaml.safe_load(yaml_in)
    print(json.dumps(schema))

if __name__ == '__main__':
    main()