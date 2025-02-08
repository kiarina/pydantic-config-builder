"""Tests for ConfigBuilder."""
import pytest
import yaml

from pydantic_config_builder.builder import ConfigBuilder
from pydantic_config_builder.config import ConfigModel


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
    """Test simple merge of two files."""
    config = ConfigModel(
        files={
            str(temp_dir / "output.yaml"): [
                str(temp_dir / "base.yaml"),
                str(temp_dir / "overlay.yaml"),
            ]
        }
    )

    builder = ConfigBuilder(config=config, base_dir=temp_dir)
    builder.build_all()

    output_path = temp_dir / "output.yaml"
    assert output_path.exists()

    with open(output_path) as f:
        result = yaml.safe_load(f)

    assert result == {
        "database": {
            "host": "localhost",
            "port": 5433,
            "credentials": {"username": "admin", "password": "secret"},
        },
        "logging": {"level": "info", "format": "json"},
    }


def test_file_not_found(temp_dir):
    """Test error when source file not found."""
    config = ConfigModel(
        files={
            str(temp_dir / "output.yaml"): [
                str(temp_dir / "nonexistent.yaml"),
            ]
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
        files={
            str(temp_dir / "second.yaml"): [
                str(first_output),
                str(temp_dir / "overlay.yaml"),
            ]
        }
    )

    builder = ConfigBuilder(config=config, base_dir=temp_dir)
    builder.build_all()

    output_path = temp_dir / "second.yaml"
    assert output_path.exists()

    with open(output_path) as f:
        result = yaml.safe_load(f)

    assert "base" in result
    assert "first" in result
    assert "database" in result
    assert "logging" in result
