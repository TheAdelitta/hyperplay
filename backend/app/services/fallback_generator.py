import json
from pathlib import Path

from app.models.simulation import SimulationSpec
from app.services.specification_validator import validate_specification

FIXTURE_PATH = (
    Path(__file__).resolve().parents[3] / "contracts" / "examples" / "projectile-motion.json"
)


def load_demo_spec() -> SimulationSpec:
    data = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return validate_specification(SimulationSpec.model_validate(data))


class FallbackSimulationGenerator:
    async def generate(self, _source_text: str) -> SimulationSpec:
        return load_demo_spec()
