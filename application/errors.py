"""Falhas de aplicação; a apresentação decide como traduzi-las para HTTP."""


class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class ValidationError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass
