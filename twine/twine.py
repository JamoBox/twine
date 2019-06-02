import os
import sys

import click
from git import Repo

from .pkg_conf import PkgConfig


PKGCONF = None


@click.command()
@click.option('--yes/--no', default=False, help='Auto-say yes')
@click.argument('package')
def update(yes, package):
    pkg = PKGCONF.get(package)
    if not pkg:
        raise click.ClickException(
                f'Package "{package}" does not exist in config.'
        )
    repo = Repo.init(pkg.get('path'))
    assert not repo.bare
    origin = repo.remotes.origin
    repo.git.checkout(pkg.get('branch'))
    info = origin.fetch(refspec=pkg.get('branch'))[0]
    if info.commit == repo.commit():
        click.echo('No updates available.')
        sys.exit(0)


@click.group()
@click.option('--config-file')
@click.option('--debug/--no-debug', default=False)
def twine(config_file, debug):
    global PKGCONF
    config_file = config_file if config_file \
            else f'{os.path.expanduser("~")}/.twine.json'
    if debug:
        import pudb; pu.db
    if not os.path.isfile(config_file):
        raise click.ClickException(f'Config file "{config_file}" does not exist.')
    PKGCONF = PkgConfig(config_file)
    PKGCONF.load_cache()

twine.add_command(update)
