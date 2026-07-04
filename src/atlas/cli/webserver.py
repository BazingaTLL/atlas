from __future__ import annotations

import click

from atlas.logging import create_logger

__all__ = ("webserver",)


@click.command(name="start")
@click.option("--host", "-h", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", "-p", default=8000, type=int, help="Port to bind the server to.")
@click.option(
    "--log-level",
    "-l",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Set the logging level.",
)
def start(host, port, log_level: str):
    """
    Start atlas webserver.
    """
    create_logger(level=log_level)
    click.echo(f"Log level set to {log_level.upper()}.")


@click.group(name="webserver")
def webserver():
    """
    atlas webserver handler
    """


webserver.add_command(start)
