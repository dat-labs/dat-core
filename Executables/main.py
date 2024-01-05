'''
Ref: https://docs.airbyte.com/understanding-airbyte/airbyte-protocol-docker

Interfaces to be defined:
 - /path/to/executable read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > message_stream.json

'''

import sys
from importlib import import_module
import click
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DatCatalog


@click.group()
def cli():
    pass


@cli.command()
@click.option('--config', '-cfg', type=click.File(), required=True)
def discover(config):
    config_mdl = ConnectorSpecification.model_validate_json(config.read())
    SourceClass = getattr(
        import_module(f'connectors.sources.source_{config_mdl.name.lower()}.source'), config_mdl.name)
    catalog = SourceClass().discover(config=config_mdl)
    click.echo(catalog.model_dump_json())


@cli.command()
@click.option('--config', '-cfg', type=click.File(), required=True)
@click.option('--catalog', '-ctlg', type=click.File(), required=True)
def read(config, catalog):
    config_mdl = ConnectorSpecification.model_validate_json(config.read())
    SourceClass = getattr(
        import_module(f'connectors.sources.source_{config_mdl.name.lower()}.source'), config_mdl.name)
    
    catalog_mdl = DatCatalog.model_validate_json(catalog.read())
    doc_generator = SourceClass().read(
        config=config_mdl, catalog=catalog_mdl)
    for doc in doc_generator:
        click.echo(doc.model_dump_json())


@cli.command()
@click.option('--config', '-cfg', type=click.File(), required=True)
def generate(config):
    from pydantic_models.dat_message import DatMessage, Type
    from pydantic_models.dat_message import DatDocumentMessage, Data

    config_mdl = ConnectorSpecification.model_validate_json(config.read())
    SourceClass = getattr(import_module(f'connectors.generators.base'), config_mdl.name)
    
    for line in sys.stdin:
        e = SourceClass().generate(
            config=config_mdl,
            dat_message=DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk=line,
                    ),
                    emitted_at=1,
                ),
            )
        )
        for vector in e:
            click.echo(vector.model_dump_json())


if __name__ == '__main__':
    cli()
