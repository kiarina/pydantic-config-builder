"""Command line interface for pydantic-config-builder."""
from pathlib import Path

import click
import yaml

from .builder import ConfigBuilder
from .config import ConfigModel


@click.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Configuration file path",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output",
)
def main(config: Path | None, verbose: bool) -> None:
    """Build YAML configurations by merging multiple files."""
    # Use default config file if not specified
    if config is None:
        config = Path("pydantic_config_builder.yml")
        if not config.exists():
            raise click.ClickException(
                "No configuration file specified and "
                "pydantic_config_builder.yml not found in current directory"
            )

    if verbose:
        click.echo(f"Using configuration file: {config}")

    # Load configuration
    try:
        with open(config, "r") as f:
            config_data = yaml.safe_load(f)
    except Exception as err:
        raise click.ClickException(f"Failed to load configuration file: {err}") from err

    # Parse configuration
    try:
        config_model = ConfigModel(files=config_data)
    except Exception as err:
        raise click.ClickException(f"Invalid configuration format: {err}") from err

    # Build configurations
    try:
        builder = ConfigBuilder(
            config=config_model,
            base_dir=config.parent,
            verbose=verbose,
        )
        builder.build_all()
    except Exception as err:
        raise click.ClickException(f"Failed to build configurations: {err}") from err

    if verbose:
        click.echo("Configuration build completed successfully")
