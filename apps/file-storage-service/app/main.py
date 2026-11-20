import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from .config import Settings
from .auth import require_auth
from .observability import metrics_response, observe_request
from .queue import StorageConsumer
from .tracing import configure_tracing

STORAGE_ROOT = Path("/storage")
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


@asynccontextmanager
async def lifespan(application: FastAPI):
    configure_tracing()
    application.state.settings = Settings()
    consumer = StorageConsumer(
        application.state.settings.rabbitmq_url,
        STORAGE_ROOT,
    )
    await consumer.start()
    application.state.storage_consumer = consumer
    try:
        yield
    finally:
        await consumer.close()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Library File Storage Service",
        version="1.0.0",
        root_path="/file-storage",
        lifespan=lifespan,
    )
    application.middleware("http")(observe_request)
    return application


app = create_app()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return metrics_response()


@app.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    _: str | None = Depends(require_auth),
) -> dict[str, str]:
    filename = file.filename or ""
    if not SAFE_FILENAME.fullmatch(filename):
        raise HTTPException(status_code=400, detail="invalid filename")

    STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    destination = (STORAGE_ROOT / filename).resolve()
    if destination.parent != STORAGE_ROOT.resolve():
        raise HTTPException(status_code=400, detail="invalid filename")
    destination.write_bytes(await file.read())
    return {"filename": filename}


@app.get("/files/{filename}")
async def download_file(
    filename: str,
    _: str | None = Depends(require_auth),
) -> FileResponse:
    if not SAFE_FILENAME.fullmatch(filename):
        raise HTTPException(status_code=404, detail="file not found")
    path = STORAGE_ROOT / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, filename=filename, media_type="text/csv")
