"""Command line interface for pydantic-config-builder."""
from pathlib import Path

import click
import yaml

from .builder import ConfigBuilder
from .config import ConfigModel


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
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
        # Try both .yaml and .yml extensions
        for ext in [".yaml", ".yml"]:
            config = Path(f"pydantic-config-builder{ext}")
            if config.exists():
                break
        else:
            raise click.ClickException(
                "No configuration file specified and neither "
                "pydantic-config-builder.yaml nor pydantic-config-builder.yml "
                "found in current directory"
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
        # Convert old format to new format if necessary
        if not any(
            isinstance(v, dict) and "input" in v and "output" in v for v in config_data.values()
        ):
            # Old format: Convert to new format
            builds = {}
            for output_path, input_paths in config_data.items():
                group_name = str(
                    Path(output_path).stem
                )  # Use filename without extension as group name
                builds[group_name] = {
                    "input": input_paths,
                    "output": [output_path],
                }
            config_data = builds

        config_model = ConfigModel(builds=config_data)
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
