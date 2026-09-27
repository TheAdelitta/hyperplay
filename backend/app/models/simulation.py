from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

ID_PATTERN = r"^[a-z][a-z0-9_]*$"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TemplateKind(StrEnum):
    RELATIONSHIP_LAB = "relationship_lab"


class VisualizationKind(StrEnum):
    TRAJECTORY = "trajectory"
    LINE = "line"
    BAR = "bar"
    METER = "meter"


class ChallengeOperator(StrEnum):
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    EQUALS = "equals"
    BETWEEN = "between"


class SourceEvidence(StrictModel):
    text: str = Field(min_length=1, max_length=500)
    location: str = Field(min_length=1, max_length=100)


class Variable(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    label: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=240)
    min: float
    max: float
    step: float = Field(gt=0)
    defaultValue: float
    unit: str = Field(max_length=30)

    @model_validator(mode="after")
    def validate_bounds(self) -> "Variable":
        if self.min >= self.max:
            raise ValueError("variable min must be less than max")
        if not self.min <= self.defaultValue <= self.max:
            raise ValueError("defaultValue must be inside variable bounds")
        return self


class Metric(StrictModel):
    id: str = Field(pattern=ID_PATTERN)
    label: str = Field(min_length=1, max_length=80)
    expression: str = Field(min_length=1, max_length=500)
    unit: str = Field(max_length=30)
    precision: int = Field(default=1, ge=0, le=6)


class Visualization(StrictModel):
    kind: VisualizationKind
    primaryMetricId: str = Field(pattern=ID_PATTERN)
    secondaryMetricId: str | None = Field(default=None, pattern=ID_PATTERN)


class Challenge(StrictModel):
    prompt: str = Field(min_length=1, max_length=300)
    metricId: str = Field(pattern=ID_PATTERN)
    operator: ChallengeOperator
    target: list[float] = Field(min_length=1, max_length=2)
    hint: str = Field(min_length=1, max_length=240)
    successMessage: str = Field(min_length=1, max_length=240)

    @model_validator(mode="after")
    def validate_target(self) -> "Challenge":
        if self.operator == ChallengeOperator.BETWEEN:
            if len(self.target) != 2 or self.target[0] >= self.target[1]:
                raise ValueError("between requires two ordered target values")
        elif len(self.target) != 1:
            raise ValueError("comparison operator requires exactly one target value")
        return self


class SimulationSpec(StrictModel):
    version: str = Field(pattern=r"^1\.0$")
    id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    template: TemplateKind
    title: str = Field(min_length=1, max_length=100)
    concept: str = Field(min_length=1, max_length=240)
    learningObjective: str = Field(min_length=1, max_length=300)
    sourceSummary: str = Field(min_length=1, max_length=600)
    sourceEvidence: list[SourceEvidence] = Field(min_length=1, max_length=3)
    variables: list[Variable] = Field(min_length=2, max_length=3)
    metrics: list[Metric] = Field(min_length=1, max_length=6)
    visualization: Visualization
    challenge: Challenge
    explanationTemplate: str = Field(min_length=1, max_length=500)
    warnings: list[str] = Field(default_factory=list, max_length=5)

    @model_validator(mode="after")
    def validate_references_and_ids(self) -> "SimulationSpec":
        variable_ids = [variable.id for variable in self.variables]
        metric_ids = [metric.id for metric in self.metrics]
        if len(variable_ids) != len(set(variable_ids)):
            raise ValueError("variable IDs must be unique")
        if len(metric_ids) != len(set(metric_ids)):
            raise ValueError("metric IDs must be unique")
        metric_id_set = set(metric_ids)
        referenced = {
            self.visualization.primaryMetricId,
            self.challenge.metricId,
        }
        if self.visualization.secondaryMetricId:
            referenced.add(self.visualization.secondaryMetricId)
        missing = referenced - metric_id_set
        if missing:
            raise ValueError(f"unknown metric references: {sorted(missing)}")
        return self


class HealthResponse(StrictModel):
    status: str = "ok"
    version: str = "1.0"
    aiConfigured: bool
