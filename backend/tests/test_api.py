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
