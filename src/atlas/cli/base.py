from __future__ import annotations

import click

from atlas import __version__
from atlas.cli.webserver import webserver


@click.group(name="atlas")
def main():
    click.echo(get_banner())


main.add_command(webserver)


def get_banner() -> str:
    return r"""
         _______  _                  _____
     /\ |__   __|| |         /\     / ____|
    /  \   | |   | |        /  \   | (___
   / /\ \  | |   | |       / /\ \   \___ \
  / ____ \ | |   | |____  / ____ \  ____) |
 /_/    \_\|_|   |______|/_/    \_\|_____/

version - {version}
""".format(version=__version__)


if __name__ == "__main__":
    main()
