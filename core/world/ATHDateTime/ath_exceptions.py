import traceback # Necessario per getTrace e getTraceAsString
from typing import Optional, List, Dict, Any, Type # Assicurati che Type sia importato

class ATHDateError(Exception):
    """
    Custom exception class for errors related to Anthaleja date and time operations.
    Include metodi per una maggiore analogia con la classe Error di PHP.
    """
    def __init__(self, message: str, code: int = 0, previous: Optional[BaseException] = None):
        """
        Costruttore per ATHDateError.

        Args:
            message: Il messaggio di errore.
            code: Un codice di errore numerico opzionale.
            previous: L'eccezione precedente che ha causato questo errore.
        """
        super().__init__(message)
        self.code = code
        if previous:
            self.__cause__ = previous

        # PHP Error ha queste proprietà popolate automaticamente quando l'errore occorre.
        # In Python, queste sono tipicamente derivate dal traceback al momento della cattura.
        # Le inizializziamo a None o valori di default; potrebbero essere popolate
        # manualmente se si creasse un'istanza di ATHDateError da un contesto
        # dove queste info sono note esplicitamente prima di sollevare l'eccezione.
        self._file: Optional[str] = None
        self._line: Optional[int] = None
        
        # Per popolare file e linea al momento della creazione (se possibile, ma meno comune)
        try:
            # Questo tenta di ottenere il frame chiamante, ma è fragile e potrebbe non
            # riflettere sempre il punto in cui l'ERRORE LOGICO è avvenuto.
            # Di solito, il traceback al momento del 'raise' è più affidabile.
            import inspect
            caller_frame = inspect.currentframe()
            if caller_frame and caller_frame.f_back:
                self._file = caller_frame.f_back.f_code.co_filename
                self._line = caller_frame.f_back.f_lineno
        except Exception:
            pass # Meglio non far fallire il costruttore dell'eccezione

    def getMessage(self) -> str: # Nomenclatura PHP
        """Restituisce il messaggio di errore."""
        return str(self.args[0]) if self.args else ""

    def getPrevious(self) -> Optional[BaseException]: # Nomenclatura PHP
        """
        Restituisce l'eccezione precedente che ha causato questo errore.
        """
        return self.__cause__

    def getCode(self) -> int: # Nomenclatura PHP
        """Restituisce il codice di errore."""
        return self.code

    def getFile(self) -> str: # Nomenclatura PHP
        """
        Restituisce il nome del file in cui è stato originato l'errore.
        Nota: In Python, questa informazione è più attendibilmente ottenuta
        dal traceback dell'eccezione quando viene catturata.
        Questo metodo restituisce il file del chiamante del COSTRUTTORE,
        che potrebbe non essere il punto del 'raise'.
        """
        if self._file:
            return self._file
        # Fallback se non popolato al momento della costruzione
        if self.__traceback__:
            return self.__traceback__.tb_frame.f_code.co_filename
        return "File non disponibile"


    def getLine(self) -> int: # Nomenclatura PHP
        """
        Restituisce il numero di linea in cui è stato originato l'errore.
        Nota: Come per getFile(), questa è più attendibilmente ottenuta dal traceback.
        Restituisce la linea del chiamante del COSTRUTTORE.
        """
        if self._line is not None:
            return self._line
        # Fallback se non popolato al momento della costruzione
        if self.__traceback__:
            return self.__traceback__.tb_lineno
        return 0

    def getTrace(self) -> List[Dict[str, Any]]: # Nomenclatura PHP
        """
        Restituisce lo stack trace come un array di dizionari (formato simile a PHP).
        Nota: Richiede che l'eccezione sia stata sollevata e abbia un traceback.
        """
        if self.__traceback__:
            trace_list = []
            for frame_summary in traceback.extract_tb(self.__traceback__):
                trace_list.append({
                    "file": frame_summary.filename,
                    "line": frame_summary.lineno,
                    "function": frame_summary.name,
                    # PHP trace include 'class' e 'type' (-> o ::)
                    # e 'args'. Ottenerli in modo identico è più complesso.
                    # Questo è un adattamento semplificato.
                })
            return trace_list
        return []

    def getTraceAsString(self) -> str: # Nomenclatura PHP
        """
        Restituisce lo stack trace come stringa.
        Nota: Richiede che l'eccezione sia stata sollevata e abbia un traceback.
        """
        if self.__traceback__:
            return "".join(traceback.format_tb(self.__traceback__))
        return "Traceback non disponibile"

    def __str__(self) -> str:
        """Rappresentazione stringa dell'errore (come PHP __toString)."""
        # Potresti voler personalizzare questo per includere file/linea se popolati,
        # ma la rappresentazione standard di Exception è solitamente sufficiente.
        # Per una maggiore analogia a PHP, che include il trace in __toString:
        # base_str = f"ATHDateError: [{self.code}] {self.getMessage()} in {self.getFile()}:{self.getLine()}\nStack trace:\n{self.getTraceAsString()}"
        # return base_str
        return f"ATHDateError: [{self.code}] {self.getMessage()}"

    # __clone non è necessario in Python perché gli oggetti non vengono clonati
    # con un metodo clone() come in PHP. La copia (shallow/deep) è gestita diversamente.

# Puoi definire le altre classi di errore ereditando da questa:
class ATHDateObjectError(ATHDateError):
    """Eccezione per errori specifici degli oggetti ATHDateTime."""
    pass

class ATHDateRangeError(ATHDateError):
    """Eccezione per errori specifici relativi a intervalli di date."""
    pass