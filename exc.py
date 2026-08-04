class AttemptsExcededError(Exception):
    pass


class InvalidOtpError(Exception):
    pass


class ProtectedEntityError(Exception):
    pass


class EmptyTableError(Exception):
    pass


class DuplicateError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass

        
class IdentificatorError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class CredentialsError(Exception):
    pass