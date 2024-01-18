'''
Ref: https://docs.airbyte.com/understanding-airbyte/airbyte-protocol-docker

Interfaces to be defined:
 - /path/to/executable read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > src_message_stream.json
 - cat src_message_stream.json | /path/to/executable generate --config <config-file-path> [--state <state-file-path>] > gen_message_stream.json

'''

import sys
import json
from time import time
from importlib import import_module
import click
from pydantic_models.connector_specification import ConnectorSpecification
from pydantic_models.dat_catalog import DatCatalog

MAX_LEN_ROWS_BUFFER = 9

@click.group()
def cli():
    '''Entry point'''


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
    SourceClass = getattr(
        import_module(f'connectors.generators.generator_{config_mdl.name.lower()}.generator'), config_mdl.name)

    for line in sys.stdin:
        try:
            json_line = json.loads(line)
        except json.decoder.JSONDecodeError as _e:
            # click.echo(f'{_e}: {line}', err=True)
            continue
        if json_line['type'] not in ['RECORD',]:
            click.echo(line)
            continue
        e = SourceClass().generate(
            config=config_mdl,
            dat_message=DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk=json_line['record'][
                            'data']['document_chunk'],
                        metadata=json_line['record'][
                            'data']['metadata'],
                    ),
                    emitted_at=int(time()),
                ),
            )
        )
        for vector in e:
            click.echo(vector.model_dump_json())


@cli.command()
@click.option('--config', '-cfg', type=click.File(), required=True)
@click.option('--catalog', '-ctlg', type=click.File(), required=True)
def write(config, catalog):
    from pydantic_models.dat_message import DatMessage, Type
    from pydantic_models.dat_message import DatDocumentMessage, Data

    config_mdl = ConnectorSpecification.model_validate_json(config.read())
    SourceClass = getattr(
        import_module(f'connectors.destinations.destination_{config_mdl.name.lower()}.destination_pinecone'), config_mdl.name)
    configured_catalog = DatCatalog.model_validate_json(catalog.read())

    rows_buffer = []
    for line in sys.stdin:
        try:
            json_line = json.loads(line)
        except json.decoder.JSONDecodeError as _e:
            # click.echo(f'{_e}: {line}', err=True)
            continue
        if json_line['type'] not in ['RECORD',]:
            click.echo(line)
            continue
        rows_buffer.append(
            DatMessage(
                type=Type.RECORD,
                record=DatDocumentMessage(
                    data=Data(
                        document_chunk=json_line['record'][
                            'data']['document_chunk'],
                        vectors=json_line['record'][
                            'data']['vectors'],
                        metadata=json_line['record'][
                            'data']['metadata'],
                    ),
                    emitted_at=int(time()),
                    namespace="Seeder",
                    stream="S3",
                )
            )
        )
        if len(rows_buffer) < MAX_LEN_ROWS_BUFFER:
            continue
        e = SourceClass().write(
            config=config_mdl,
            configured_catalog=configured_catalog,
            input_messages=rows_buffer,
        )
        for m in e:
            click.echo(m.model_dump_json())
        rows_buffer = []
    if len(rows_buffer):
        e = SourceClass().write(
            config=config_mdl,
            configured_catalog=configured_catalog,
            input_messages=rows_buffer,
        )
        for m in e:
            click.echo(m.model_dump_json())



if __name__ == '__main__':
    cli()
