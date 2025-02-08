"""Configuration model for pydantic-config-builder."""
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, Field


class ConfigModel(BaseModel):
    """Configuration model for build settings."""

    files: Dict[str, List[str]] = Field(
        description="Dictionary of output file paths and their source files",
    )

    def resolve_path(self, path: str, base_dir: Path) -> Path:
        """Resolve relative/absolute path."""
        if path.startswith("~"):
            return Path(path).expanduser()
        if Path(path).is_absolute():
            return Path(path)
        return base_dir / path

    def get_resolved_config(self, base_dir: Path) -> Dict[Path, List[Path]]:
        """Get resolved configuration with absolute paths."""
        return {
            self.resolve_path(out_path, base_dir): [
                self.resolve_path(src_path, base_dir) for src_path in src_paths
            ]
            for out_path, src_paths in self.files.items()
        }
