from contextvars import ContextVar
from typing import Any

# The "invisible backpack" used to track deep execution state across jobs.
# Exceptions and Loggers can read this globally without parameter passing.
app_context: ContextVar[dict[str, Any]] = ContextVar("app_context", default={})
