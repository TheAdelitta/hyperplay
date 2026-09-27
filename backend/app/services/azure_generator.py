import json

from openai import AsyncAzureOpenAI
from pydantic import ValidationError

from app.core.config import Settings
from app.core.errors import ApiError
from app.models.simulation import SimulationSpec
from app.prompts.simulation_prompt import SYSTEM_PROMPT
from app.services.specification_validator import UnsafeExpressionError, validate_specification


class AzureSimulationGenerator:
    def __init__(self, settings: Settings) -> None:
        self.deployment = settings.azure_openai_deployment
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

    async def generate(self, source_text: str) -> SimulationSpec:
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "Create a SimulationSpec from the source below.\n\n"
                            f"SOURCE_START\n{source_text}\nSOURCE_END"
                        ),
                    },
                ],
            )
            content = response.choices[0].message.content or ""
            data = json.loads(content)
            if data.get("unsupported") is True:
                raise ApiError(
                    "UNSUPPORTED_CONCEPT",
                    data.get("reason", "This material does not fit the current simulation type."),
                    422,
                )
            return validate_specification(SimulationSpec.model_validate(data))
        except ApiError:
            raise
        except (json.JSONDecodeError, ValidationError, UnsafeExpressionError) as exc:
            raise ApiError(
                "INVALID_SIMULATION_SPEC",
                "The AI returned a simulation that failed validation.",
                502,
            ) from exc
        except Exception as exc:
            raise ApiError(
                "AI_GENERATION_FAILED",
                "Hyperplay could not generate a simulation right now.",
                502,
            ) from exc
