"""Relationship Lab contract (v2). Mirrors frontend/src/lib/games/lab/types.ts.

Model output is parsed leniently (unknown fields are ignored) because the validator
repairs what it can; structure that cannot be repaired still fails here.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

KEY_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"


class LenientModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class LabControl(LenientModel):
    key: str = Field(pattern=KEY_PATTERN, max_length=24)
    label: str = Field(min_length=1, max_length=80)
    unit: str = Field(default="", max_length=30)
    min: float
    max: float
    step: float
    default: float
    decimals: int = Field(default=1, ge=0, le=6)


class LabReadout(LenientModel):
    label: str = Field(min_length=1, max_length=80)
    expression: str = Field(min_length=1, max_length=300)
    unit: str = Field(default="", max_length=30)
    decimals: int = Field(default=1, ge=0, le=6)


class LabSeries(LenientModel):
    variable: str = Field(pattern=KEY_PATTERN, max_length=24)
    label: str = Field(min_length=1, max_length=80)
    unit: str = Field(default="", max_length=30)
    min: float
    max: float
    steps: int = Field(default=120, ge=10, le=500)
    expression: str = Field(min_length=1, max_length=300)
    markAt: float | None = None


class LabOutput(LenientModel):
    label: str = Field(min_length=1, max_length=80)
    unit: str = Field(default="", max_length=30)
    decimals: int = Field(default=1, ge=0, le=6)
    min: float
    max: float


class StageTarget(LenientModel):
    value: float
    tolerance: float


class StageLock(LenientModel):
    key: str = Field(max_length=24)
    value: float
    note: str = Field(default="This control is fixed for this challenge", max_length=160)


class LabStage(LenientModel):
    challenge: str = Field(min_length=1, max_length=300)
    teaches: str = Field(min_length=1, max_length=200)
    target: StageTarget
    lock: StageLock | None = None
    hints: list[str] = Field(default_factory=list, max_length=5)
    debriefing: str = Field(min_length=1, max_length=600)


class LabLevel(LenientModel):
    gameType: Literal["lab"] = "lab"
    visualMode: Literal["trajectory", "curve", "fill", "meter"]
    concept: str = Field(min_length=1, max_length=200)
    sourceSummary: str = Field(min_length=1, max_length=600)
    formula: str = Field(min_length=1, max_length=200)
    expression: str = Field(min_length=1, max_length=300)
    controls: list[LabControl] = Field(min_length=2, max_length=2)
    constants: dict[str, float] = Field(default_factory=dict)
    output: LabOutput
    stages: list[LabStage] = Field(min_length=1, max_length=4)
    series: LabSeries | None = None
    readouts: list[LabReadout] = Field(default_factory=list)
    completion: str = Field(default="", max_length=600)
    difficulty: Literal["middle", "high", "college"] = "high"
    subject: str = Field(default="", max_length=60)
    courseLabel: str = Field(default="", max_length=120)

    @field_validator("readouts")
    @classmethod
    def keep_three_readouts(cls, readouts: list[LabReadout]) -> list[LabReadout]:
        return readouts[:3]


class UnfittableResult(LenientModel):
    gameType: Literal["unfittable"] = "unfittable"
    reason: str = Field(min_length=1, max_length=400)
    suggestion: str = Field(min_length=1, max_length=400)
