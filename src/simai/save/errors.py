class SaveError(Exception):
    """Errore base per le operazioni di salvataggio."""


class SaveNotFoundError(SaveError):
    """Il file di salvataggio non esiste."""


class SaveFormatError(SaveError):
    """Il file esiste ma il formato è invalido o corrotto."""


class SaveVersionError(SaveError):
    """Il file è stato prodotto da una versione non supportata."""

    def __init__(self, file_version: int, supported: int) -> None:
        super().__init__(
            f"Versione salvataggio non supportata: file={file_version}, supportata<={supported}"
        )
        self.file_version = file_version
        self.supported = supported
