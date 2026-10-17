import re
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

STORAGE_ROOT = Path("/storage")
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

app = FastAPI(
    title="Library File Storage Service",
    version="1.0.0",
    root_path="/file-storage",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
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
async def download_file(filename: str) -> FileResponse:
    if not SAFE_FILENAME.fullmatch(filename):
        raise HTTPException(status_code=404, detail="file not found")
    path = STORAGE_ROOT / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path, filename=filename, media_type="text/csv")
