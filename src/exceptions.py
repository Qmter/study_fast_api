from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models import ExceptionModel


class CustomUnauthorizedException(HTTPException):
    def __init__(self, status_code: int, detail: str, message: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message

class CustomNotFoundException(HTTPException):
    def __init__(self, status_code: int, detail: str, message: str):
        super().__init__(status_code=status_code, detail=detail)
        self.message = message


def register_exception_handlers(app):
    @app.exception_handler(CustomUnauthorizedException)
    async def custom_unauthorized_exception(request: Request, exc: CustomUnauthorizedException):
        error = jsonable_encoder(ExceptionModel(status_code=exc.status_code, detail=exc.detail, message=exc.message))
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                'status_code': 401,
                'detail': exc.detail,
                'message': exc.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.exception_handler(CustomNotFoundException)
    async def custom_not_found_exception(request: Request, exc: CustomNotFoundException):
        error = jsonable_encoder(ExceptionModel(status_code=exc.status_code, detail=exc.detail, message=exc.message))
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'status_code': 404,
                'detail': exc.detail,
                'message': exc.message
            }
        )