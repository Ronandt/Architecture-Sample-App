class ApplicationException(Exception):
    """Base class for all custom app errors"""
    def __init__(self, message: str, http_status: int = 500, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.http_status = http_status
        self.details = details or {}


class InvalidItemTitle(ApplicationException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, http_status=400, details=  details)

class InvalidItemDescription(ApplicationException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, http_status=400, details=  details)

class DatabaseUnavaliable(ApplicationException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message = message, http_status=500, details=details)

class ItemNotFound(ApplicationException):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message=message, http_status=404, details=  details)