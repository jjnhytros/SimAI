import hashlib
import json
import zlib
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from simai.__version__ import __version__
from simai.save.errors import (
    SaveFormatError,
    SaveVersionError,
)

MAGIC = b"SIMAI\x00"
SUPPORTED_VERSION = 1
SAV_FORMAT_NAME = "simai-sav"


@dataclass(frozen=True)
class SaveHeader:
    version: int
    created_at: str
    simai_version: str
    schema_revision: str | None
    checksum: str
    tick_index: int
    master_seed: int


def _canonical_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def encode(
    payload: dict[str, Any],
    *,
    tick_index: int,
    master_seed: int,
    schema_revision: str | None,
) -> bytes:
    """Codifica un payload in formato .sav binario."""
    payload_bytes = _canonical_json(payload)
    checksum = hashlib.sha256(payload_bytes).hexdigest()
    compressed = zlib.compress(payload_bytes, level=6)

    header = {
        "format": SAV_FORMAT_NAME,
        "version": SUPPORTED_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "simai_version": __version__,
        "schema_revision": schema_revision,
        "checksum": checksum,
        "tick_index": tick_index,
        "master_seed": master_seed,
    }
    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")

    return (
        MAGIC
        + SUPPORTED_VERSION.to_bytes(2, "big")
        + len(header_bytes).to_bytes(4, "big")
        + header_bytes
        + compressed
    )


def decode(data: bytes) -> tuple[SaveHeader, dict[str, Any]]:
    """Decodifica un file .sav, verificando magic, versione e checksum."""
    min_len = len(MAGIC) + 2 + 4
    if len(data) < min_len:
        raise SaveFormatError("File troppo corto per essere un .sav")

    if not data.startswith(MAGIC):
        raise SaveFormatError("Magic non valido: non è un file SimAI")

    offset = len(MAGIC)
    file_version = int.from_bytes(data[offset : offset + 2], "big")
    offset += 2
    if file_version != SUPPORTED_VERSION:
        raise SaveVersionError(file_version, SUPPORTED_VERSION)

    header_len = int.from_bytes(data[offset : offset + 4], "big")
    offset += 4

    if len(data) < offset + header_len:
        raise SaveFormatError("Header troncato")

    header_bytes = data[offset : offset + header_len]
    offset += header_len

    try:
        header_dict = json.loads(header_bytes)
    except json.JSONDecodeError as exc:
        raise SaveFormatError(f"Header JSON invalido: {exc}") from exc

    if header_dict.get("format") != SAV_FORMAT_NAME:
        raise SaveFormatError("Formato header non riconosciuto")

    compressed = data[offset:]
    try:
        payload_bytes = zlib.decompress(compressed)
    except zlib.error as exc:
        raise SaveFormatError(f"Payload compresso invalido: {exc}") from exc

    expected = header_dict.get("checksum")
    actual = hashlib.sha256(payload_bytes).hexdigest()
    if expected != actual:
        raise SaveFormatError("Checksum non corrispondente: file corrotto o manomesso")

    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError as exc:
        raise SaveFormatError(f"Payload JSON invalido: {exc}") from exc

    header = SaveHeader(
        version=file_version,
        created_at=str(header_dict.get("created_at", "")),
        simai_version=str(header_dict.get("simai_version", "")),
        schema_revision=header_dict.get("schema_revision"),
        checksum=expected,
        tick_index=int(header_dict.get("tick_index", 0)),
        master_seed=int(header_dict.get("master_seed", 0)),
    )
    return header, payload
