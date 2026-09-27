from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.errors import ApiError
from app.prompts.lab_prompt import Difficulty
from app.services.document_extractor import extract_pdf_text
from app.services.lab_generator import AzureLabGenerator, LabGenerator, level_cache

router = APIRouter(prefix="/labs", tags=["labs"])

SOURCE_HEADER = "X-HyperPlay-Source"


def get_lab_generator(settings: Settings = Depends(get_settings)) -> LabGenerator | None:
    return AzureLabGenerator(settings) if settings.ai_configured else None


@router.post(
    "/generate",
    summary="Generate a Relationship Lab level from a chapter",
    responses={
        200: {"description": "A LabLevel, or an UnfittableResult when the chapter has no "
              "two-variable relationship. The X-HyperPlay-Source header is `generated` or "
              "`cache` (a level previously generated from this same file)."},
    },
)
async def generate_lab(
    subject: Annotated[str, Form(min_length=1, max_length=60)],
    gradeLevel: Annotated[Difficulty, Form()],
    course: Annotated[str, Form(max_length=120)] = "",
    text: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
    settings: Settings = Depends(get_settings),
    generator: LabGenerator | None = Depends(get_lab_generator),
) -> JSONResponse:
    if not (text and text.strip()) and file is None:
        raise ApiError("MISSING_SOURCE", "Provide pasted text or a PDF file.", 400)

    parts: list[str] = []
    if text and text.strip():
        parts.append(" ".join(text.split()))
    if file is not None:
        parts.append(await extract_pdf_text(file, settings.max_upload_mb * 1024 * 1024))
    source_text = "\n\n".join(parts).strip()[: settings.max_source_characters]
    if len(source_text) < 200:
        raise ApiError(
            "EMPTY_DOCUMENT",
            "There isn't enough readable text in this material to build a level.",
            422,
        )

    course_label = course.strip() or subject
    cache_key = level_cache.key(source_text, subject, gradeLevel)
    try:
        if generator is None:
            raise ApiError(
                "AI_NOT_CONFIGURED",
                "Live AI generation is not configured. Try a sample level instead.",
                503,
            )
        result = await generator.generate(source_text, subject, course_label, gradeLevel)
    except ApiError as exc:
        cached = level_cache.get(cache_key) if exc.status_code >= 500 else None
        if cached is None:
            raise
        return JSONResponse(cached, headers={SOURCE_HEADER: "cache"})

    payload = result.model_dump(mode="json", exclude_none=True)
    if payload["gameType"] == "lab":
        level_cache.put(cache_key, payload)
    return JSONResponse(payload, headers={SOURCE_HEADER: "generated"})
