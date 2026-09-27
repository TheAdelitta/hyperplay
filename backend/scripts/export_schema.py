import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.simulation import SimulationSpec

destination = Path(__file__).resolve().parents[2] / "contracts" / "simulation-spec.schema.json"
destination.write_text(
    json.dumps(SimulationSpec.model_json_schema(), indent=2) + "\n",
    encoding="utf-8",
)
print(destination)
