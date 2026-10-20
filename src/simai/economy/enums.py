from enum import StrEnum


class JobTitle(StrEnum):
    BARISTA = "barista"
    INSEGNANTE = "insegnante"
    COMMESSO = "commesso"
    STUDENTE = "studente"


class TransactionKind(StrEnum):
    SALARY = "salary"
    PURCHASE = "purchase"
