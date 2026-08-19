from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
import json


@dataclass
class CatalogEntry:
    name: str
    module_path: Optional[str] = None
    class_name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class CatalogService:
    """Simple JSON-backed catalog service for strategy metadata and module paths.

    Stores a dict of name -> CatalogEntry as JSON. Designed to be lightweight and
    to support dynamic importing of strategy classes by module path + class name.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._entries: Dict[str, CatalogEntry] = {}
        if self.path.exists():
            try:
                self._load()
            except Exception:
                # If the file exists but is invalid, don't crash — start empty
                self._entries = {}

    def _load(self):
        data = json.loads(self.path.read_text())
        self._entries = {k: CatalogEntry(**v) for k, v in data.items()}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v.__dict__ for k, v in self._entries.items()}
        self.path.write_text(json.dumps(serializable, indent=2, sort_keys=True))

    def register(self, entry: CatalogEntry):
        self._entries[entry.name] = entry
        self.save()

    def unregister(self, name: str):
        if name in self._entries:
            del self._entries[name]
            self.save()

    def get(self, name: str) -> Optional[CatalogEntry]:
        return self._entries.get(name)

    def list(self) -> Dict[str, CatalogEntry]:
        return dict(self._entries)
