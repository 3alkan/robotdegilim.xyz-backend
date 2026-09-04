from __future__ import annotations
from fastapi import Request, status
from fastapi.responses import JSONResponse
from dataclasses import dataclass
import json
import logging
import traceback
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class AppException(Exception):
    """Unified application error carrying message, API status code, context, and optional cause."""
    message: str
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str | None = None
    context: dict[str, Any] | None = None
    cause: Exception | None = None
    call_stack: str | None = None

    def __post_init__(self) -> None:
        """Capture call stack when the error object is created."""
        if self.call_stack is None:
            self.call_stack = "".join(traceback.format_stack()[:-1])

    def __str__(self) -> str:
        return self.message

    def _exc_info(self) -> tuple[type[BaseException], BaseException, Any] | None:
        """Return traceback-bearing exception info tuple when available."""
        if self.cause and getattr(self.cause, "__traceback__", None):
            return (type(self.cause), self.cause, self.cause.__traceback__)
        if getattr(self, "__traceback__", None):
            return (type(self), self, self.__traceback__)
        return None

    def to_log(self, *, include_stack: bool = False) -> dict[str, Any]:
        """Build structured log payload for this error."""
        payload = {"message": self.message}
        
        # MAGIC: Automatically grab whatever operational state we had when it crashed!
        from robotdegilim_xyz_backend.core.context import app_context
        current_ctx = app_context.get()
        if current_ctx:
            payload["app_state"] = current_ctx
            
        if self.code:
            payload["code"] = self.code
        if self.context:
            payload["context"] = self.context
        if self.cause:
            payload["cause"] = str(self.cause)
        if include_stack and self.call_stack:
            payload["stack"] = self.call_stack
        return payload

    def log(self, dest_logger: logging.Logger, level: int = logging.ERROR) -> None:
        """Log this error with optional traceback or fallback stack information."""
        exc_info = self._exc_info() if level >= logging.ERROR else None
        
        # Build the payload, skipping 'message' since it will be passed directly as the log string
        payload = self.to_log(include_stack=(exc_info is None and level >= logging.ERROR))
        if "message" in payload:
            del payload["message"]
            
        # Pass the payload inside extra={"app_error": ...} so the formatters can intercept it!
        dest_logger.log(level, self.message, extra={"app_error": payload}, exc_info=exc_info)


async def app_exception_handler(request: Request, exc: AppException):
    """
    Global handler for all AppException raised within the API.
    Logs the detailed structured error to the backend, but only returns safe message to client.
    """
    # Log the deep context to the backend logs
    exc.log(logger, logging.ERROR)
    
    # Return the clean, safe response to the API client
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
