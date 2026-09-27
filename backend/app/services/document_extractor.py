import fitz
from fastapi import UploadFile, status

from app.core.errors import ApiError


async def extract_pdf_text(file: UploadFile, max_bytes: int) -> str:
    filename = file.filename or "upload"
    if not filename.lower().endswith(".pdf") or file.content_type not in {
        "application/pdf",
        "application/octet-stream",
    }:
        raise ApiError("UNSUPPORTED_FILE", "Hyperplay currently accepts PDF files only.", 415)

    payload = await file.read(max_bytes + 1)
    if len(payload) > max_bytes:
        raise ApiError("FILE_TOO_LARGE", "The PDF exceeds the upload limit.", 413)

    try:
        document = fitz.open(stream=payload, filetype="pdf")
        if document.needs_pass:
            raise ApiError("INVALID_DOCUMENT", "Encrypted PDFs are not supported.", 422)
        text = "\n".join(page.get_text("text") for page in document)
    except ApiError:
        raise
    except Exception as exc:
        raise ApiError(
            "INVALID_DOCUMENT",
            "We could not read this PDF.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ) from exc

    normalized = " ".join(text.split())
    if not normalized:
        raise ApiError(
            "EMPTY_DOCUMENT",
            "This PDF has no extractable text. Scanned-image OCR is not supported yet.",
            422,
        )
    return normalized
