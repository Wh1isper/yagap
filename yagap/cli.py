from __future__ import annotations

import click

from yagap.agent_runtime.cli import start_agent_runtime
from yagap.gateway.cli import start_gateway


@click.group()
def cli() -> None:
    """YAGAP service CLI."""


@cli.group(name="agent-runtime")
def agent_runtime_group() -> None:
    """Agent runtime service commands."""


@agent_runtime_group.command(name="start")
@click.option("--host", type=str, default=None, help="Host override")
@click.option("--port", type=int, default=None, help="Port override")
def agent_runtime_start(host: str | None, port: int | None) -> None:
    start_agent_runtime(host=host, port=port)


@cli.group(name="gateway")
def gateway_group() -> None:
    """Gateway service commands."""


@gateway_group.command(name="start")
@click.option("--host", type=str, default=None, help="Host override")
@click.option("--port", type=int, default=None, help="Port override")
def gateway_start(host: str | None, port: int | None) -> None:
    start_gateway(host=host, port=port)


def main() -> None:
    cli()


if __name__ == "__main__":  # pragma: no cover
    main()
