"""Configuration model for pydantic-config-builder."""
import glob
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

    def _expand_glob(self, pattern: str, base_dir: Path) -> List[Path]:
        """Expand glob pattern to list of paths."""
        # パターンを絶対パスに解決
        abs_pattern = str(self.resolve_path(pattern, base_dir))
        # globで検索
        matches = glob.glob(abs_pattern, recursive=True)
        if not matches:
            print(f"Warning: No files found matching pattern: {pattern}")
            return []
        # 重複を排除して返す
        return sorted(set(Path(p) for p in matches))

    def get_resolved_config(self, base_dir: Path) -> Dict[Path, List[Path]]:
        """Get resolved configuration with absolute paths."""
        result = {}
        for out_path, src_paths in self.files.items():
            resolved_sources: List[Path] = []
            seen_paths = set()
            for src_path in src_paths:
                # ワイルドカードを含むパターンの場合は展開
                if any(c in src_path for c in "*?["):
                    paths = self._expand_glob(src_path, base_dir)
                    for path in paths:
                        if path not in seen_paths:
                            seen_paths.add(path)
                            resolved_sources.append(path)
                else:
                    path = self.resolve_path(src_path, base_dir)
                    if path not in seen_paths:
                        seen_paths.add(path)
                        resolved_sources.append(path)
            result[self.resolve_path(out_path, base_dir)] = resolved_sources
        return result
