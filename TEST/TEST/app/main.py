from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, Response
from app.middleware.error_handler import add_error_middleware
from app.routers.extract_resume import router as extract_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Lazy-load OCR on first use to reduce startup time.
    yield


app: FastAPI = FastAPI(title="OCR Resume Digitization API", version="0.1.0", lifespan=lifespan)
add_error_middleware(app)
app.include_router(extract_router)


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> Response:
    return Response(status_code=204) 