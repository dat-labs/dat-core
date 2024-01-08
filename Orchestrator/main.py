import click
from typing import Mapping
from pydantic_models.connection import Connection

_CMD_PREFIX = 'python Executables/main.py'
_CMD_GEN_MAP = {
    'source': {
        'cmd': 'read',
        'args': ['ctlg', 'cfg'],
    }
}

def _gen_cmd(actor_type: str, args: Mapping[str, str]) -> str:
    """Generate cmd line str.

    Args:
        actor_type (str): Actor type can be one of source, generator or destination
        args (Mapping): Mapping of args to their corresponding values

    Returns:
        str: cmd line str
    """
    _cmd_line_str = ''
    _cmd_line_str += _CMD_PREFIX
    _cmd_line_str += f" {_CMD_GEN_MAP[actor_type]['cmd']}"
    for arg in _CMD_GEN_MAP[actor_type]['args']:
        _cmd_line_str += ' ' + _gen_args(arg_value=args[arg], short_name=arg)
    return _cmd_line_str


def _gen_args(arg_value: str, short_name: str = None, long_name: str = None) -> str:
    """Generate arg string to be appended to a cmd. If both short_name and long_name
    are passed, short_name will be used.

    Args:
        arg_value (str): value of the argument
        short_name (str, optional): short name of the argument. Defaults to None.
        long_name (_type_, optional): long name of the argument. Defaults to None.

    Returns:
        str: _description_
    """
    _cmd = ''
    if long_name:
        _cmd += f'--{long_name}={arg_value}'
    if short_name:
        _cmd = f'-{short_name} {arg_value}'
    return _cmd

def gen_tmp_dir(func, *args):
    def wrapper():
        print(func)
        func(*args, None)
    return wrapper

@gen_tmp_dir
def foo():
    print('foo')

@gen_tmp_dir
@click.command()
@click.option('--config', '-cfg', type=click.File(), required=True)
def cli(config):
    connection_mdl = Connection.model_validate_json(config.read())
    print(connection_mdl.spec.source)
    src_cmd = _gen_cmd(
        actor_type='source',
        args={
            'ctlg': 'source_catalog.json',
            'cfg': 'source_config.json',
        }
    )
    print(src_cmd)


if __name__ == '__main__':
    cli()
    # foo()
