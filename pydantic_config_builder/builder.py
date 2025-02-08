"""YAML configuration builder."""
from pathlib import Path
from typing import Any, Dict, List

import yaml

from .config import ConfigModel


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """Load YAML file."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}


def merge_dicts(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries recursively."""
    result = base.copy()
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


class ConfigBuilder:
    """Configuration builder."""

    def __init__(self, config: ConfigModel, base_dir: Path, verbose: bool = False):
        """Initialize builder."""
        self.config = config
        self.base_dir = base_dir
        self.verbose = verbose
        self.built_configs: Dict[Path, Dict[str, Any]] = {}

    def build_config(self, output_path: Path, source_files: List[Path]) -> Dict[str, Any]:
        """Build configuration by merging source files."""
        if output_path in self.built_configs:
            if self.verbose:
                print(f"Using cached config for {output_path}")
            return self.built_configs[output_path]

        if self.verbose:
            print(f"Building config for {output_path}")
            print(f"Source files: {source_files}")

        result: Dict[str, Any] = {}
        for src_file in source_files:
            if not src_file.exists():
                raise FileNotFoundError(f"Source file not found: {src_file}")

            # If the source file is an output file, build it first
            if src_file in self.config.get_resolved_config(self.base_dir):
                src_config = self.build_config(
                    src_file, self.config.get_resolved_config(self.base_dir)[src_file]
                )
            else:
                src_config = load_yaml(src_file)

            result = merge_dicts(result, src_config)

        self.built_configs[output_path] = result
        return result

    def build_all(self) -> None:
        """Build all configurations."""
        resolved_config = self.config.get_resolved_config(self.base_dir)
        for out_path, src_files in resolved_config.items():
            if self.verbose:
                print(f"\nProcessing {out_path}")

            result = self.build_config(out_path, src_files)

            # Create parent directory if it doesn't exist
            out_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the result
            with open(out_path, "w") as f:
                yaml.dump(result, f, sort_keys=False)
