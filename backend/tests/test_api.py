import io

import fitz
from fastapi.testclient import TestClient

from app.api.simulations import get_generator
from app.main import app
from app.services.fallback_generator import FallbackSimulationGenerator

client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_is_valid() -> None:
    response = client.get("/api/v1/simulations/demo")
    assert response.status_code == 200
    assert response.json()["template"] == "relationship_lab"


def test_missing_source() -> None:
    app.dependency_overrides[get_generator] = lambda: FallbackSimulationGenerator()
    try:
        response = client.post("/api/v1/simulations/generate")
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "MISSING_SOURCE"
    finally:
        app.dependency_overrides.clear()


def test_generate_from_text_with_fallback() -> None:
    app.dependency_overrides[get_generator] = lambda: FallbackSimulationGenerator()
    try:
        response = client.post(
            "/api/v1/simulations/generate",
            data={"text": "Range depends on launch velocity, angle, and gravity."},
        )
        assert response.status_code == 200
        assert response.json()["id"] == "projectile-motion"
    finally:
        app.dependency_overrides.clear()


def test_generate_from_pdf_with_fallback() -> None:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Velocity and angle affect projectile range.")
    payload = document.tobytes()
    app.dependency_overrides[get_generator] = lambda: FallbackSimulationGenerator()
    try:
        response = client.post(
            "/api/v1/simulations/generate",
            files={"file": ("lesson.pdf", io.BytesIO(payload), "application/pdf")},
        )
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_rejects_non_pdf() -> None:
    app.dependency_overrides[get_generator] = lambda: FallbackSimulationGenerator()
    try:
        response = client.post(
            "/api/v1/simulations/generate",
            files={"file": ("lesson.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 415
        assert response.json()["error"]["code"] == "UNSUPPORTED_FILE"
    finally:
        app.dependency_overrides.clear()


def test_frontend_cache_headers(tmp_path) -> None:
    # index.html must be re-checked on every visit so a deploy shows up on a normal
    # refresh; hashed build files under assets/ can be cached forever.
    from fastapi import FastAPI

    from app.main import FrontendFiles

    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html></html>")
    (tmp_path / "assets" / "index-abc123.js").write_text("console.log(1)")
    site = FastAPI()
    site.mount("/", FrontendFiles(directory=tmp_path, html=True))
    local = TestClient(site)
    assert local.get("/").headers["cache-control"] == "no-cache"
    assert "immutable" in local.get("/assets/index-abc123.js").headers["cache-control"]
