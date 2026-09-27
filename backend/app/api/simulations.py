from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.models.simulation import SimulationSpec
from app.services.azure_generator import AzureSimulationGenerator
from app.services.document_extractor import extract_pdf_text
from app.services.fallback_generator import FallbackSimulationGenerator, load_demo_spec
from app.services.generator import SimulationGenerator

router = APIRouter(prefix="/simulations", tags=["simulations"])


def get_generator(settings: Settings = Depends(get_settings)) -> SimulationGenerator:
    if settings.ai_configured:
        return AzureSimulationGenerator(settings)
    if settings.enable_development_fallback:
        return FallbackSimulationGenerator()
    raise ApiError(
        "AI_NOT_CONFIGURED",
        "Live AI generation is not configured. Try the demo simulation instead.",
        503,
    )


@router.get("/demo", response_model=SimulationSpec)
async def demo() -> SimulationSpec:
    return load_demo_spec()


@router.post("/generate", response_model=SimulationSpec)
async def generate_simulation(
    text: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
    settings: Settings = Depends(get_settings),
    generator: SimulationGenerator = Depends(get_generator),
) -> SimulationSpec:
    if not text and file is None:
        raise ApiError("MISSING_SOURCE", "Provide pasted text or a PDF file.", 400)

    parts: list[str] = []
    if text and text.strip():
        parts.append(" ".join(text.split()))
    if file is not None:
        parts.append(await extract_pdf_text(file, settings.max_upload_mb * 1024 * 1024))

    source_text = "\n\n".join(parts).strip()
    if not source_text:
        raise ApiError("MISSING_SOURCE", "The supplied material is empty.", 400)
    source_text = source_text[: settings.max_source_characters]
    return await generator.generate(source_text)
