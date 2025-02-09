"""Tests for CLI."""
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from pydantic_config_builder.cli import main


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with test files."""
    # Create base config
    base = tmp_path / "base.yaml"
    base.write_text(
        yaml.dump(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                },
            }
        )
    )

    # Create config file
    config = tmp_path / "pydantic_config_builder.yml"
    config.write_text(
        yaml.dump(
            {
                "test": {
                    "input": ["base.yaml"],
                    "output": ["output.yaml"],
                }
            }
        )
    )

    return tmp_path


def test_cli_default_config(temp_dir):
    """Test CLI with default config file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Copy test files to current directory
        Path("pydantic-config-builder.yml").write_text(
            (temp_dir / "pydantic_config_builder.yml").read_text()
        )
        Path("base.yaml").write_text((temp_dir / "base.yaml").read_text())

        result = runner.invoke(main)
        assert result.exit_code == 0
        assert Path("output.yaml").exists()


def test_cli_custom_config(temp_dir):
    """Test CLI with custom config file."""
    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(temp_dir / "pydantic_config_builder.yml")])
    assert result.exit_code == 0
    assert (temp_dir / "output.yaml").exists()


def test_cli_verbose(temp_dir):
    """Test CLI with verbose output."""
    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(temp_dir / "pydantic_config_builder.yml"), "-v"])
    assert result.exit_code == 0
    assert "Using configuration file:" in result.output
    assert "Configuration build completed successfully" in result.output


def test_cli_no_config():
    """Test CLI with no config file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main)
        assert result.exit_code != 0
        assert "No configuration file specified" in result.output


def test_cli_invalid_config(temp_dir):
    """Test CLI with invalid config file."""
    invalid_config = temp_dir / "invalid.yml"
    invalid_config.write_text("invalid: yaml: :")

    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(invalid_config)])
    assert result.exit_code != 0
    assert "Failed to load configuration file" in result.output


def test_cli_group_filter(temp_dir):
    """Test CLI with group filter."""
    # Create config file with multiple groups
    config = temp_dir / "pydantic_config_builder.yml"
    config.write_text(
        yaml.dump(
            {
                "group1": {
                    "input": ["base.yaml"],
                    "output": ["output1.yaml"],
                },
                "group2": {
                    "input": ["base.yaml"],
                    "output": ["output2.yaml"],
                },
            }
        )
    )

    # Test building only group1
    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(config), "-g", "group1"])
    assert result.exit_code == 0
    assert (temp_dir / "output1.yaml").exists()
    assert not (temp_dir / "output2.yaml").exists()


def test_cli_multiple_groups(temp_dir):
    """Test CLI with multiple group filters."""
    # Create config file with multiple groups
    config = temp_dir / "pydantic_config_builder.yml"
    config.write_text(
        yaml.dump(
            {
                "group1": {
                    "input": ["base.yaml"],
                    "output": ["output1.yaml"],
                },
                "group2": {
                    "input": ["base.yaml"],
                    "output": ["output2.yaml"],
                },
                "group3": {
                    "input": ["base.yaml"],
                    "output": ["output3.yaml"],
                },
            }
        )
    )

    # Test building group1 and group2
    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(config), "-g", "group1", "-g", "group2"])
    assert result.exit_code == 0
    assert (temp_dir / "output1.yaml").exists()
    assert (temp_dir / "output2.yaml").exists()
    assert not (temp_dir / "output3.yaml").exists()


def test_cli_nonexistent_group(temp_dir):
    """Test CLI with nonexistent group."""
    config = temp_dir / "pydantic_config_builder.yml"
    config.write_text(
        yaml.dump(
            {
                "group1": {
                    "input": ["base.yaml"],
                    "output": ["output1.yaml"],
                }
            }
        )
    )

    runner = CliRunner()
    result = runner.invoke(main, ["-c", str(config), "-g", "nonexistent"])
    assert result.exit_code != 0
    assert "None of the specified groups" in result.output
