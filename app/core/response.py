from typing import Any, Optional, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status

class ApiResponse(BaseModel):
    """Standardized API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None

def success_response(
    data: Any = None,
    message: str = "Operation successful",
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Generate a standardized success response
    """
    response = ApiResponse(
        success=True,
        message=message,
        data=data,
        meta=meta
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True)
    )

def error_response(
    message: str = "An error occurred",
    data: Any = None,
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Generate a standardized error response
    """
    response = ApiResponse(
        success=False,
        message=message,
        data=data,
        meta=meta
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(exclude_none=True)
    )
