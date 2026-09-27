from typing import Protocol

from app.models.simulation import SimulationSpec


class SimulationGenerator(Protocol):
    async def generate(self, source_text: str) -> SimulationSpec: ...
