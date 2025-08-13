from typing import Callable
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def add_error_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def _error_middleware(request: Request, call_next: Callable):  # type: ignore[override]
        try:
            response = await call_next(request)
            return response
        except Exception as err:  # noqa: BLE001
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"}) 