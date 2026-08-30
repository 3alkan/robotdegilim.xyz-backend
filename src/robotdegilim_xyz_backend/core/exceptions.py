from fastapi import Request, status
from fastapi.responses import JSONResponse

class AppException(Exception):
    """Base class for all application-specific exceptions."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

async def app_exception_handler(request: Request, exc: AppException):
    """
    Global handler for all AppException raised within the application.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
