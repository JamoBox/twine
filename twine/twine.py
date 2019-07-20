import os
import sys
import subprocess
import logging

import click
import structlog
from structlogger import configure_logger
from git import Repo

from .pkg_conf import PkgConfig


PKGCONF = None

configure_logger(log_to_file=False)
logging.Logger('twine').setLevel(logging.INFO)
LOG = structlog.get_logger('twine')

SAFE_COMMIT = None


def _rollback(pkg):
    repo = Repo.init(pkg.get('path'))
    repo.git.checkout(SAFE_COMMIT)
    _run_post_install(pkg, first_run=False)


def _run_post_install(pkg, first_run=True):
    LOG.info('Running post-install scripts..')
    cmds = pkg.get('build_cmds')
    try:
        curr_cmd = None
        for cmd in cmds:
            curr_cmd = cmd
            LOG.info('Running command..', cmd=cmd)
            proc = subprocess.run(cmd, cwd=pkg.get('path'),
                                  stderr=subprocess.STDOUT, shell=True, text=True)
            click.echo(proc.stdout)
    except Exception as e:
        LOG.error('Execption occured during post-install', cmd=curr_cmd, exc=e)
        if click.confirm('Rollback to safe state?'):
            _rollback(pkg)
    LOG.info('Update complete')


@click.command()
@click.option('--yes/--no', default=False, help='Auto-say yes')
@click.argument('package')
def update(yes, package):
    global SAFE_COMMIT
    LOG.info('Checking for package in config..',
             package=package, config=PKGCONF.path)
    pkg = PKGCONF.get(package)
    if not pkg:
        raise click.ClickException(
                f'Package "{package}" does not exist in config.'
        )
    repo = Repo.init(pkg.get('path'))
    SAFE_COMMIT = repo.commit()
    assert not repo.bare
    origin = repo.remotes.origin
    branch = pkg.get('branch')
    LOG.info('Checking out branch..', branch=branch)
    repo.git.checkout(branch)
    LOG.info('Fetching from remote..', branch=branch, remote=origin)
    info = origin.fetch(refspec=branch)[0]
    if info.commit == repo.commit():
        click.echo('No updates available.')
        sys.exit(0)
    else:
        LOG.info('Update available', commit=info.commit)
        if yes or click.confirm('Continue?'):
            LOG.info('Pulling updates..')
            origin.pull()
            _run_post_install(pkg)


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
