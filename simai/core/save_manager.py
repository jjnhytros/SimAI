"""SaveManager — creazione/caricamento/eliminazione di salvataggi `.sav`.

Formato `.sav` (binario, self-describing):

    [0:10]    magic: b"SIMAI_SAV\\x00"                      (10 byte)
    [10:12]   file_format_version: uint16 little-endian     (2 byte)
    [12:16]   header_len: uint32 little-endian              (4 byte)
    [16:16+N] header: JSON UTF-8 (N = header_len)           (N byte)
    [16+N:]   payload: bytes                                (M byte)

Il payload è il dump binario del DB SQLite (bytes del file), passato per:
  1. compressione zstd (se `zstandard` installato)
  2. cifratura Fernet (se `SIMAI_SAVE_ENCRYPTION_KEY` configurata)

L'header JSON contiene i metadati del salvataggio (nome, versione, seed,
datetime Anthalys, ecc.). È leggibile senza decifrare il payload.

Non è un singleton. Ogni istanza riceve il suo `saves_dir` e opzionalmente
il path del DB sorgente (se si vuole usare `create_save` senza passare bytes).
"""

from __future__ import annotations

import hashlib
import importlib
import json
import re
import struct
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from loguru import logger

from simai.__version__ import __version__

# --- Costanti formato -------------------------------------------------------

MAGIC: Final[bytes] = b"SIMAI_SAV\x00"
FILE_FORMAT_VERSION: Final[int] = 1
_FIXED_HEADER_SIZE: Final[int] = len(MAGIC) + 2 + 4  # magic + uint16 + uint32

# --- Dipendenze opzionali ---------------------------------------------------


_HAS_ZSTD: bool = False
zstd: Any = None
try:
    zstd = importlib.import_module("zstandard")
    _HAS_ZSTD = True
except ImportError:
    pass


_HAS_FERNET: bool = False
_Fernet: Any = None
_InvalidToken: Any = Exception
try:
    _fernet_module = importlib.import_module("cryptography.fernet")
    _Fernet = _fernet_module.Fernet
    _InvalidToken = _fernet_module.InvalidToken
    _HAS_FERNET = True
except ImportError:
    pass


# --- Dataclasses ------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SaveInfo:
    """Metadati di un salvataggio (dall'header, senza toccare il payload)."""

    save_id: int
    name: str
    file_path: Path
    file_size: int
    payload_hash: str
    created_at: datetime
    simai_version: str
    git_sha: str | None
    seed: int
    tick_index: int
    anthalys_datetime: str
    encrypted: bool
    compressed: bool
    db_size: int


@dataclass(frozen=True, slots=True)
class SimulationState:
    """Stato di simulazione ripristinato da un salvataggio.

    Attualmente contiene solo il path al DB SQLite ripristinato. In fasi
    successive (FASE 3+) conterrà anche entità parsate (Character, Location,
    ecc.).
    """

    info: SaveInfo
    db_path: Path


# --- Eccezioni --------------------------------------------------------------


class SaveError(Exception):
    """Errore generico su operazioni di salvataggio."""


class SaveNotFoundError(SaveError):
    """Salvataggio non trovato."""


class SaveFormatError(SaveError):
    """Formato `.sav` non valido o corrotto."""


# --- Helpers ----------------------------------------------------------------

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    s = s.lower().strip()
    s = _SLUG_RE.sub("-", s).strip("-")
    return s or "save"


def _now_ms() -> int:
    return int(time.time() * 1000)


# --- SaveManager ------------------------------------------------------------


class SaveManager:
    """Gestisce creazione, lista, caricamento ed eliminazione di salvataggi."""

    def __init__(
        self,
        saves_dir: Path,
        *,
        db_source_path: Path | None = None,
        encryption_key: str = "",
        compression_level: int = 10,
    ) -> None:
        if compression_level < 1 or compression_level > 22:
            raise ValueError(f"compression_level deve essere 1..22, ricevuto {compression_level}")
        self._saves_dir = saves_dir
        self._saves_dir.mkdir(parents=True, exist_ok=True)
        self._db_source_path = db_source_path
        self._compression_level = compression_level
        self._fernet: Any = None

        if encryption_key:
            if not _HAS_FERNET:
                raise SaveError(
                    "SIMAI_SAVE_ENCRYPTION_KEY presente ma cryptography non installato. "
                    "Installa con: uv sync --extra save"
                )
            try:
                self._fernet = _Fernet(encryption_key.encode("ascii"))
            except Exception as exc:
                raise SaveError(f"Chiave di cifratura non valida: {exc}") from exc

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def saves_dir(self) -> Path:
        return self._saves_dir

    @property
    def encryption_enabled(self) -> bool:
        return self._fernet is not None

    @property
    def compression_available(self) -> bool:
        return _HAS_ZSTD

    # ------------------------------------------------------------------
    # create_save
    # ------------------------------------------------------------------

    def create_save(
        self,
        name: str,
        *,
        seed: int = 0,
        tick_index: int = 0,
        anthalys_datetime: str = "",
        git_sha: str | None = None,
        db_bytes: bytes | None = None,
    ) -> SaveInfo:
        """Crea un salvataggio. Se ``db_bytes`` è None, legge da ``db_source_path``."""
        if db_bytes is None:
            if self._db_source_path is None:
                raise SaveError("db_source_path non configurato e db_bytes non fornito")
            if not self._db_source_path.exists():
                raise SaveError(f"DB sorgente non trovato: {self._db_source_path}")
            db_bytes = self._db_source_path.read_bytes()

        # 1. Compressione
        if _HAS_ZSTD:
            payload = zstd.ZstdCompressor(level=self._compression_level).compress(db_bytes)
            compressed = True
        else:
            payload = db_bytes
            compressed = False

        # 2. Cifratura
        encrypted = False
        if self._fernet is not None:
            payload = self._fernet.encrypt(payload)
            encrypted = True

        payload_hash = hashlib.sha256(payload).hexdigest()

        # 3. ID + path
        save_id = _now_ms()
        slug = _slugify(name)
        file_path = self._saves_dir / f"{save_id}_{slug}.sav"
        counter = 1
        while file_path.exists():
            counter += 1
            file_path = self._saves_dir / f"{save_id}_{slug}_{counter}.sav"

        # 4. Header
        created_at = datetime.now().replace(microsecond=0)
        header: dict[str, Any] = {
            "file_format_version": FILE_FORMAT_VERSION,
            "name": name,
            "slug": slug,
            "save_id": save_id,
            "simai_version": __version__,
            "git_sha": git_sha,
            "seed": seed,
            "tick_index": tick_index,
            "anthalys_datetime": anthalys_datetime,
            "created_at": created_at.isoformat(timespec="seconds"),
            "encrypted": encrypted,
            "compressed": compressed,
            "payload_size": len(payload),
            "payload_hash": payload_hash,
            "db_size": len(db_bytes),
        }
        header_json = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(header_json) > 0xFFFFFFFF:
            raise SaveError("Header troppo grande (> 4 GiB)")

        with file_path.open("wb") as f:
            f.write(MAGIC)
            f.write(struct.pack("<H", FILE_FORMAT_VERSION))
            f.write(struct.pack("<I", len(header_json)))
            f.write(header_json)
            f.write(payload)

        file_size = file_path.stat().st_size
        logger.info(
            "Creato salvataggio '{}' (id={}, {} B, encrypted={}, compressed={})",
            name,
            save_id,
            file_size,
            encrypted,
            compressed,
        )

        return SaveInfo(
            save_id=save_id,
            name=name,
            file_path=file_path,
            file_size=file_size,
            payload_hash=payload_hash,
            created_at=created_at,
            simai_version=__version__,
            git_sha=git_sha,
            seed=seed,
            tick_index=tick_index,
            anthalys_datetime=anthalys_datetime,
            encrypted=encrypted,
            compressed=compressed,
            db_size=len(db_bytes),
        )

    # ------------------------------------------------------------------
    # list_saves
    # ------------------------------------------------------------------

    def list_saves(self) -> list[SaveInfo]:
        """Elenca tutti i `.sav` in ``saves_dir``, ordinati per data decrescente."""
        result: list[SaveInfo] = []
        for p in sorted(self._saves_dir.glob("*.sav")):
            try:
                result.append(self._read_header(p))
            except SaveFormatError as exc:
                logger.warning("Salvataggio illeggibile {}: {}", p, exc)
        result.sort(key=lambda s: s.created_at, reverse=True)
        return result

    # ------------------------------------------------------------------
    # load_save
    # ------------------------------------------------------------------

    def load_save(
        self,
        save_id: int,
        *,
        target_db_path: Path | None = None,
    ) -> SimulationState:
        """Ripristina un salvataggio su un DB SQLite.

        Se ``target_db_path`` è None, scrive in ``saves_dir / f"loaded_{save_id}.db"``.
        """
        info = self._find_by_id(save_id)

        with info.file_path.open("rb") as f:
            # Offset esatti:
            #   [0:10]    MAGIC
            #   [10:12]   uint16 file_format_version
            #   [12:16]   uint32 header_len
            #   [16:16+N] header JSON (N = header_len)
            #   [16+N:]   payload
            f.seek(len(MAGIC) + 2)  # skip magic + version -> offset 12
            len_raw = f.read(4)  # legge header_len (offset 12-15)
            (header_len,) = struct.unpack("<I", len_raw)
            f.seek(_FIXED_HEADER_SIZE + header_len)  # offset 16 + N
            payload = f.read()

        actual_hash = hashlib.sha256(payload).hexdigest()
        if actual_hash != info.payload_hash:
            raise SaveFormatError(
                f"Hash mismatch per save_id={save_id}: "
                f"atteso {info.payload_hash[:12]}..., calcolato {actual_hash[:12]}..."
            )

        if info.encrypted:
            if self._fernet is None:
                raise SaveError(
                    "Salvataggio cifrato ma nessuna chiave configurata (SIMAI_SAVE_ENCRYPTION_KEY)"
                )
            try:
                payload = self._fernet.decrypt(payload)
            except _InvalidToken as exc:
                raise SaveError("Chiave di cifratura errata o file corrotto") from exc

        if info.compressed:
            if not _HAS_ZSTD:
                raise SaveError(
                    "Salvataggio compresso ma zstandard non installato. "
                    "Installa con: uv sync --extra save"
                )
            payload = zstd.ZstdDecompressor().decompress(payload)

        if target_db_path is None:
            target_db_path = self._saves_dir / f"loaded_{save_id}.db"
        target_db_path.parent.mkdir(parents=True, exist_ok=True)
        target_db_path.write_bytes(payload)

        logger.info(
            "Ripristinato salvataggio id={} in {} ({} B)",
            save_id,
            target_db_path,
            len(payload),
        )

        return SimulationState(info=info, db_path=target_db_path)

    # ------------------------------------------------------------------
    # delete_save
    # ------------------------------------------------------------------

    def delete_save(self, save_id: int) -> None:
        """Elimina un salvataggio dal filesystem."""
        info = self._find_by_id(save_id)
        info.file_path.unlink()
        logger.info("Eliminato salvataggio '{}' (id={})", info.name, save_id)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _find_by_id(self, save_id: int) -> SaveInfo:
        for info in self.list_saves():
            if info.save_id == save_id:
                return info
        raise SaveNotFoundError(f"Salvataggio con id={save_id} non trovato")

    def _read_header(self, path: Path) -> SaveInfo:
        with path.open("rb") as f:
            magic = f.read(len(MAGIC))
            if magic != MAGIC:
                raise SaveFormatError(f"Magic non valido in {path.name}")
            ver_bytes = f.read(2)
            if len(ver_bytes) != 2:
                raise SaveFormatError(f"File troncato (version) in {path.name}")
            (file_format_version,) = struct.unpack("<H", ver_bytes)
            if file_format_version != FILE_FORMAT_VERSION:
                raise SaveFormatError(f"Versione formato non supportata: {file_format_version}")
            len_bytes = f.read(4)
            if len(len_bytes) != 4:
                raise SaveFormatError(f"File troncato (header_len) in {path.name}")
            (header_len,) = struct.unpack("<I", len_bytes)
            header_bytes = f.read(header_len)
            if len(header_bytes) != header_len:
                raise SaveFormatError(f"Header troncato in {path.name}")

        try:
            header = json.loads(header_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SaveFormatError(f"Header JSON non valido in {path.name}: {exc}") from exc

        try:
            from simai.utils import (
                coerce_int,
                coerce_optional_str,
                coerce_str,
            )

            created_at = datetime.fromisoformat(coerce_str(header["created_at"], name="created_at"))
            return SaveInfo(
                save_id=coerce_int(header["save_id"], name="save_id"),
                name=coerce_str(header["name"], name="name"),
                file_path=path,
                file_size=path.stat().st_size,
                payload_hash=coerce_str(header["payload_hash"], name="payload_hash"),
                created_at=created_at,
                simai_version=coerce_str(header["simai_version"], name="simai_version"),
                git_sha=coerce_optional_str(header.get("git_sha"), name="git_sha"),
                seed=coerce_int(header["seed"], name="seed"),
                tick_index=coerce_int(header["tick_index"], name="tick_index"),
                anthalys_datetime=coerce_str(header["anthalys_datetime"], name="anthalys_datetime"),
                encrypted=bool(header["encrypted"]),
                compressed=bool(header["compressed"]),
                db_size=coerce_int(header["db_size"], name="db_size"),
            )
        except (KeyError, ValueError) as exc:
            raise SaveFormatError(f"Header incompleto in {path.name}: {exc}") from exc
