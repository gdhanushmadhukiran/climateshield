"""Custom API exceptions and handlers for ClimateShield."""

from typing import Optional, Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class APIException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class EntityNotFoundException(APIException):
    def __init__(self, entity_name: str, entity_id: str):
        super().__init__(
            code=f"{entity_name.upper()}_NOT_FOUND",
            message=f"{entity_name} '{entity_id}' was not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidStateTransitionException(APIException):
    def __init__(self, from_state: str, to_state: str):
        super().__init__(
            code="INVALID_STATE_TRANSITION",
            message=f"Cannot transition incident from '{from_state}' to '{to_state}'",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    content = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": request_id,
        }
    }
    if exc.details:
        content["error"]["details"] = exc.details
    return JSONResponse(status_code=exc.status_code, content=content)


from fastapi.encoders import jsonable_encoder


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request payload",
                "request_id": request_id,
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the request",
                "request_id": request_id,
            }
        },
    )
