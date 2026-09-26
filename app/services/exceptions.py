"""Custom domain exceptions (translated to HTTP responses in the API layer)."""


class DomainError(Exception):
    """Base class for business-rule violations."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ReaderNotFoundError(DomainError):
    pass


class DuplicateTicketNumberError(DomainError):
    pass


class TicketAlreadyConfiscatedError(DomainError):
    pass


class TicketNotIssuedError(DomainError):
    pass


class BookNotOnHandError(DomainError):
    pass


class EmptyUpdateError(DomainError):
    pass
