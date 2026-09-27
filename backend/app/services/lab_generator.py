import hashlib
import json
import logging
from collections import OrderedDict
from typing import Protocol

from openai import AsyncAzureOpenAI
from pydantic import ValidationError

from app.core.config import Settings
from app.core.errors import ApiError
from app.models.lab import LabLevel, UnfittableResult
from app.prompts.lab_prompt import LAB_SYSTEM_PROMPT, Difficulty, build_lab_user_message
from app.services.lab_validator import validate_lab_level

logger = logging.getLogger("hyperplay.labs")

LabResult = LabLevel | UnfittableResult

DEFAULT_UNFIT_REASON = "This chapter has no two-variable relationship to explore."
DEFAULT_UNFIT_SUGGESTION = "Try a chapter built around a formula, a rate, or a graph."


class LabGenerator(Protocol):
    async def generate(
        self, source_text: str, subject: str, course_label: str, difficulty: Difficulty
    ) -> LabResult: ...


def _strip_fences(content: str) -> str:
    return content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()


def parse_lab_response(
    content: str, subject: str, course_label: str, difficulty: Difficulty
) -> LabResult:
    """Turn raw model JSON into a validated level or an unfittable result."""
    try:
        data = json.loads(_strip_fences(content))
        if not isinstance(data, dict):
            raise ValueError("response is not a JSON object")
        if data.get("gameType") == "unfittable" or data.get("unsupported") is True:
            return UnfittableResult(
                reason=data.get("reason") or DEFAULT_UNFIT_REASON,
                suggestion=data.get("suggestion") or DEFAULT_UNFIT_SUGGESTION,
            )
        # We already know these from the upload screen; don't let the model guess them.
        data.update(subject=subject, courseLabel=course_label, difficulty=difficulty)
        level = LabLevel.model_validate(data)
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        logger.warning("lab response failed to parse: %s", exc)
        raise ApiError(
            "INVALID_SIMULATION_SPEC", "The AI returned a level that failed validation.", 502
        ) from exc

    result = validate_lab_level(level)
    logger.info("lab validation ok=%s problems=%s", result.ok, result.problems)
    if not result.ok:
        raise ApiError(
            "INVALID_SIMULATION_SPEC",
            "The AI returned a level that could not be made winnable.",
            502,
            details=result.problems,
        )
    return result.level


class AzureLabGenerator:
    def __init__(self, settings: Settings) -> None:
        self.deployment = settings.azure_openai_deployment
        # Low tokens-per-minute quotas return 429 under bursts; the SDK backs off and
        # honours Retry-After, so a few more retries ride out a short spike.
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            max_retries=4,
            timeout=60,
        )

    async def generate(
        self, source_text: str, subject: str, course_label: str, difficulty: Difficulty
    ) -> LabResult:
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": LAB_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": build_lab_user_message(
                            source_text, subject, course_label, difficulty
                        ),
                    },
                ],
            )
        except Exception as exc:
            logger.warning("Azure OpenAI call failed: %s", exc)
            raise ApiError(
                "AI_GENERATION_FAILED", "HyperPlay could not generate a level right now.", 502
            ) from exc
        content = response.choices[0].message.content or ""
        return parse_lab_response(content, subject, course_label, difficulty)


class LevelCache:
    """Last good level per (file, subject, level), in memory only.

    If Azure fails mid-demo, re-uploading the same chapter replays the level that was
    genuinely generated from it. Nothing is written to disk and no documents are kept.
    """

    def __init__(self, capacity: int = 64) -> None:
        self.capacity = capacity
        self._items: OrderedDict[str, dict] = OrderedDict()

    @staticmethod
    def key(source_text: str, subject: str, difficulty: str) -> str:
        return hashlib.sha256(f"{subject}\x00{difficulty}\x00{source_text}".encode()).hexdigest()

    def get(self, key: str) -> dict | None:
        if key in self._items:
            self._items.move_to_end(key)
        return self._items.get(key)

    def put(self, key: str, payload: dict) -> None:
        self._items[key] = payload
        self._items.move_to_end(key)
        while len(self._items) > self.capacity:
            self._items.popitem(last=False)

    def clear(self) -> None:
        self._items.clear()


level_cache = LevelCache()
