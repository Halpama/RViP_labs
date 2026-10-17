import pytest
from httpx import ASGITransport, AsyncClient

from app import main


@pytest.mark.asyncio
async def test_upload_and_download_file(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "STORAGE_ROOT", tmp_path)
    async with AsyncClient(
        transport=ASGITransport(app=main.app),
        base_url="http://test",
    ) as client:
        upload = await client.post(
            "/files",
            files={"file": ("report.csv", b"id,name\n1,Alice\n", "text/csv")},
        )
        assert upload.status_code == 201
        assert upload.json() == {"filename": "report.csv"}

        download = await client.get("/files/report.csv")
        assert download.status_code == 200
        assert download.content == b"id,name\n1,Alice\n"


@pytest.mark.asyncio
async def test_upload_rejects_path_traversal():
    async with AsyncClient(
        transport=ASGITransport(app=main.app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/files",
            files={"file": ("../report.csv", b"bad", "text/csv")},
        )
    assert response.status_code == 400
