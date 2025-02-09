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


def test_glob_pattern(tmp_path):
    """Test glob pattern in source files."""
    # Create test files
    (tmp_path / "config-1.yaml").touch()
    (tmp_path / "config-2.yaml").touch()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir/config-3.yaml").touch()

    config = ConfigModel(
        files={
            "output.yaml": ["config-*.yaml", "**/config-*.yaml"],
        }
    )

    resolved = config.get_resolved_config(tmp_path)

    assert len(resolved) == 1
    output_path = tmp_path / "output.yaml"
    assert output_path in resolved
    assert len(resolved[output_path]) == 3
    assert resolved[output_path][0] == tmp_path / "config-1.yaml"
    assert resolved[output_path][1] == tmp_path / "config-2.yaml"
    assert resolved[output_path][2] == tmp_path / "subdir/config-3.yaml"


def test_glob_pattern_no_match(tmp_path):
    """Test glob pattern with no matching files."""
    config = ConfigModel(
        files={
            "output.yaml": ["nonexistent-*.yaml"],
        }
    )

    resolved = config.get_resolved_config(tmp_path)

    assert len(resolved) == 1
    output_path = tmp_path / "output.yaml"
    assert output_path in resolved
    assert len(resolved[output_path]) == 0
