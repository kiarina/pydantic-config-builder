"""Tests for ConfigModel."""
from pathlib import Path

from pydantic_config_builder.config import ConfigModel


def test_resolve_absolute_path():
    """Test resolving absolute path."""
    config = ConfigModel(files={})
    path = "/absolute/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path("/absolute/path")


def test_resolve_relative_path():
    """Test resolving relative path."""
    config = ConfigModel(files={})
    path = "relative/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path("/base/dir/relative/path")


def test_resolve_home_path():
    """Test resolving path with home directory."""
    config = ConfigModel(files={})
    path = "~/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path.home() / "path"


def test_get_resolved_config():
    """Test getting resolved configuration."""
    config = ConfigModel(
        files={
            "output.yaml": ["base.yaml", "/abs/path.yaml", "~/home.yaml"],
        }
    )
    base_dir = Path("/base/dir")

    resolved = config.get_resolved_config(base_dir)

    assert len(resolved) == 1
    output_path = base_dir / "output.yaml"
    assert output_path in resolved
    assert len(resolved[output_path]) == 3
    assert resolved[output_path][0] == base_dir / "base.yaml"
    assert resolved[output_path][1] == Path("/abs/path.yaml")
    assert resolved[output_path][2] == Path.home() / "home.yaml"
