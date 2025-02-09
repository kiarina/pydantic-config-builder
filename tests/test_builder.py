"""Tests for ConfigBuilder."""
import pytest
import yaml

from pydantic_config_builder.builder import ConfigBuilder
from pydantic_config_builder.config import BuildConfig, ConfigModel


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory with test files."""
    base = tmp_path / "base.yaml"
    base.write_text(
        yaml.dump(
            {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "credentials": {"username": "admin"},
                },
                "logging": {"level": "info"},
            }
        )
    )

    overlay = tmp_path / "overlay.yaml"
    overlay.write_text(
        yaml.dump(
            {
                "database": {
                    "port": 5433,
                    "credentials": {"password": "secret"},
                },
                "logging": {"format": "json"},
            }
        )
    )

    return tmp_path


def test_merge_simple(temp_dir):
    """Test simple merge of two files with multiple outputs."""
    config = ConfigModel(
        builds={
            "test": BuildConfig(
                input=[
                    str(temp_dir / "base.yaml"),
                    str(temp_dir / "overlay.yaml"),
                ],
                output=[
                    str(temp_dir / "output1.yaml"),
                    str(temp_dir / "output2.yaml"),
                ],
            )
        }
    )

    builder = ConfigBuilder(config=config, base_dir=temp_dir)
    builder.build_all()

    expected = {
        "database": {
            "host": "localhost",
            "port": 5433,
            "credentials": {"username": "admin", "password": "secret"},
        },
        "logging": {"level": "info", "format": "json"},
    }

    # Check both output files
    for output_path in [temp_dir / "output1.yaml", temp_dir / "output2.yaml"]:
        assert output_path.exists()
        with open(output_path) as f:
            result = yaml.safe_load(f)
        assert result == expected


def test_file_not_found(temp_dir):
    """Test error when source file not found."""
    config = ConfigModel(
        builds={
            "test": BuildConfig(
                input=[str(temp_dir / "nonexistent.yaml")],
                output=[str(temp_dir / "output.yaml")],
            )
        }
    )

    builder = ConfigBuilder(config=config, base_dir=temp_dir)
    with pytest.raises(FileNotFoundError):
        builder.build_all()


def test_build_with_built_config(temp_dir):
    """Test using a built config as a source for another config."""
    # First config
    first_output = temp_dir / "first.yaml"
    first_output.write_text(
        yaml.dump(
            {
                "base": {"value": 1},
                "first": {"value": 2},
            }
        )
    )

    # Second config using first as base
    config = ConfigModel(
        builds={
            "test": BuildConfig(
                input=[
                    str(first_output),
                    str(temp_dir / "overlay.yaml"),
                ],
                output=[
                    str(temp_dir / "second1.yaml"),
                    str(temp_dir / "second2.yaml"),
                ],
            )
        }
    )

    builder = ConfigBuilder(config=config, base_dir=temp_dir)
    builder.build_all()

    # Check both output files
    for output_path in [temp_dir / "second1.yaml", temp_dir / "second2.yaml"]:
        assert output_path.exists()
        with open(output_path) as f:
            result = yaml.safe_load(f)
        assert "base" in result
        assert "first" in result
        assert "database" in result
        assert "logging" in result
