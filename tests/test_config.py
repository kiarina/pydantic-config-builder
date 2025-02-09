"""Tests for ConfigModel."""
from pathlib import Path

from pydantic_config_builder.config import BuildConfig, ConfigModel


def test_resolve_absolute_path():
    """Test resolving absolute path."""
    config = ConfigModel(builds={})
    path = "/absolute/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path("/absolute/path")


def test_resolve_relative_path():
    """Test resolving relative path."""
    config = ConfigModel(builds={})
    path = "relative/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path("/base/dir/relative/path")


def test_resolve_home_path():
    """Test resolving path with home directory."""
    config = ConfigModel(builds={})
    path = "~/path"
    base_dir = Path("/base/dir")

    resolved = config.resolve_path(path, base_dir)
    assert resolved == Path.home() / "path"


def test_get_resolved_config():
    """Test getting resolved configuration."""
    config = ConfigModel(
        builds={
            "test_group": BuildConfig(
                input=["base.yaml", "/abs/path.yaml", "~/home.yaml"],
                output=["output1.yaml", "output2.yaml"],
            )
        }
    )
    base_dir = Path("/base/dir")

    resolved = config.get_resolved_config(base_dir)

    assert len(resolved) == 2
    output_path1 = base_dir / "output1.yaml"
    output_path2 = base_dir / "output2.yaml"
    assert output_path1 in resolved
    assert output_path2 in resolved
    assert len(resolved[output_path1]) == 3
    assert len(resolved[output_path2]) == 3
    for output_path in [output_path1, output_path2]:
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
        builds={
            "test_group": BuildConfig(
                input=["config-*.yaml", "**/config-*.yaml"],
                output=["output1.yaml", "output2.yaml"],
            )
        }
    )

    resolved = config.get_resolved_config(tmp_path)

    assert len(resolved) == 2
    output_path1 = tmp_path / "output1.yaml"
    output_path2 = tmp_path / "output2.yaml"
    assert output_path1 in resolved
    assert output_path2 in resolved
    for output_path in [output_path1, output_path2]:
        assert len(resolved[output_path]) == 3
        assert resolved[output_path][0] == tmp_path / "config-1.yaml"
        assert resolved[output_path][1] == tmp_path / "config-2.yaml"
        assert resolved[output_path][2] == tmp_path / "subdir/config-3.yaml"


def test_glob_pattern_no_match(tmp_path):
    """Test glob pattern with no matching files."""
    config = ConfigModel(
        builds={
            "test_group": BuildConfig(
                input=["nonexistent-*.yaml"],
                output=["output.yaml"],
            )
        }
    )

    resolved = config.get_resolved_config(tmp_path)

    assert len(resolved) == 1
    output_path = tmp_path / "output.yaml"
    assert output_path in resolved
    assert len(resolved[output_path]) == 0
