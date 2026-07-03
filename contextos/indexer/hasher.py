"""File hashing utilities for incremental indexing."""

from pathlib import Path
import hashlib


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    """Compute the SHA-256 hash for a file without loading it all at once."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()
