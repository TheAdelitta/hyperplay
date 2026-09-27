import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import TypeAdapter

from app.models.lab import LabLevel, UnfittableResult
from app.models.simulation import SimulationSpec

contracts = Path(__file__).resolve().parents[2] / "contracts"
schemas = {
    "simulation-spec.schema.json": SimulationSpec.model_json_schema(),
    "lab-level.schema.json": TypeAdapter(LabLevel | UnfittableResult).json_schema(),
}
for name, schema in schemas.items():
    destination = contracts / name
    destination.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(destination)
