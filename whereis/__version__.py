"""The versioning system."""
from pathlib import Path

_version_file: Path = Path(__file__).parent.parent / "VERSION"
__version__: str = _version_file.read_text().strip()
