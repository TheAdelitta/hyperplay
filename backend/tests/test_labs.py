import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api.labs import get_lab_generator
from app.core.errors import ApiError
from app.main import app
from app.models.lab import LabLevel, UnfittableResult
from app.services.lab_expression import UnsafeExpressionError, compile_expression
from app.services.lab_generator import level_cache, parse_lab_response
from app.services.lab_validator import output_function, validate_lab_level

EXAMPLES = Path(__file__).resolve().parents[2] / "contracts" / "examples" / "labs"
CHAPTER = "Pressure, volume and temperature are linked by the ideal gas law PV = nRT. " * 5
client = TestClient(app)


def load(name: str) -> dict:
    return json.loads((EXAMPLES / f"{name}.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _isolate():
    level_cache.clear()
    yield
    app.dependency_overrides.clear()
    level_cache.clear()


# ---------------------------------------------------------------- expressions


def test_caret_is_power_with_normal_precedence() -> None:
    assert compile_expression("2 ^ 3 * 2", [])({}) == 16
    assert compile_expression("P * (1 + r / 100) ^ t", ["P", "r", "t"])(
        {"P": 1000, "r": 5, "t": 2}
    ) == pytest.approx(1102.5)


@pytest.mark.parametrize(
    "expression",
    ["__import__('os')", "x.real", "open('f')", "[x]", "x if x else 1", "unknown * 2", "'a'"],
)
def test_unsafe_expressions_are_rejected(expression: str) -> None:
    with pytest.raises(UnsafeExpressionError):
        compile_expression(expression, ["x"])


# ------------------------------------------------------------------ validator


@pytest.mark.parametrize("name", ["physics", "chemistry", "biology", "mathematics"])
def test_verified_levels_pass_unchanged(name: str) -> None:
    level = LabLevel.model_validate(load(name))
    result = validate_lab_level(level)
    assert result.ok, result.problems
    assert result.problems == []
    assert result.level.model_dump() == level.model_dump()


def test_matches_front_end_outputs() -> None:
    math_level = LabLevel.model_validate(load("mathematics"))
    assert output_function(math_level)({**math_level.constants, "r": 8, "t": 21}) == pytest.approx(
        5033.83, abs=0.01
    )


def test_unreachable_target_is_clamped_and_still_winnable() -> None:
    raw = load("chemistry")
    raw["stages"][0]["target"]["value"] = 5000
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.ok
    assert any("clamped" in p for p in result.problems)
    assert result.level.stages[0].target.value < 60


def test_unknown_lock_is_removed() -> None:
    raw = load("chemistry")
    raw["stages"][0]["lock"]["key"] = "Q"
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.ok
    assert result.level.stages[0].lock is None


def test_lock_snaps_to_slider_step() -> None:
    raw = load("mathematics")
    raw["stages"][0]["lock"]["value"] = 5.2  # step is 0.5
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.level.stages[0].lock.value == 5.0


def test_level_that_cannot_be_evaluated_is_rejected() -> None:
    raw = load("chemistry")
    raw["expression"] = "log(-P)"
    assert not validate_lab_level(LabLevel.model_validate(raw)).ok


# ------------------------------------------------------------- model parsing


def test_parse_unfittable() -> None:
    content = '{"gameType": "unfittable", "reason": "A war narrative.", "suggestion": "Physics."}'
    result = parse_lab_response(content, "History", "World History", "high")
    assert isinstance(result, UnfittableResult)


def test_parse_strips_fences_and_uses_request_context() -> None:
    raw = load("chemistry")
    raw["subject"] = "Wrong"
    content = "```json\n" + json.dumps(raw) + "\n```"
    result = parse_lab_response(content, "Chemistry", "Chem I", "college")
    assert isinstance(result, LabLevel)
    context = (result.subject, result.courseLabel, result.difficulty)
    assert context == ("Chemistry", "Chem I", "college")


def test_parse_garbage_is_a_502() -> None:
    with pytest.raises(ApiError) as exc:
        parse_lab_response("not json", "Chemistry", "Chem I", "high")
    assert exc.value.status_code == 502


# ------------------------------------------------------------------- endpoint


class FakeGenerator:
    def __init__(self, result=None, error: ApiError | None = None) -> None:
        self.result, self.error = result, error

    async def generate(self, *_args):
        if self.error:
            raise self.error
        return self.result


def post(**data):
    form = {"subject": "Chemistry", "gradeLevel": "high", "course": "Chem I", "text": CHAPTER}
    form.update(data)
    return client.post("/api/v1/labs/generate", data=form)


def test_not_configured_is_503() -> None:
    app.dependency_overrides[get_lab_generator] = lambda: None
    response = post()
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AI_NOT_CONFIGURED"


def test_generated_level_is_returned_and_labelled() -> None:
    level = LabLevel.model_validate(load("chemistry"))
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator(level)
    response = post()
    assert response.status_code == 200
    assert response.headers["X-HyperPlay-Source"] == "generated"
    assert response.json()["gameType"] == "lab"
    assert "lock" not in response.json()["stages"][2]


def test_failure_replays_level_generated_from_same_file() -> None:
    level = LabLevel.model_validate(load("chemistry"))
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator(level)
    assert post().status_code == 200

    down = ApiError("AI_GENERATION_FAILED", "down", 502)
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator(error=down)
    replay = post()
    assert replay.status_code == 200
    assert replay.headers["X-HyperPlay-Source"] == "cache"

    other_file = post(text=CHAPTER + " A different chapter.")
    assert other_file.status_code == 502


def test_unfittable_is_200_and_not_cached() -> None:
    unfit = UnfittableResult(reason="Narrative.", suggestion="Try physics.")
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator(unfit)
    response = post(subject="History")
    assert response.status_code == 200
    assert response.json()["gameType"] == "unfittable"


def test_too_little_text_is_422() -> None:
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator()
    response = post(text="Too short.")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "EMPTY_DOCUMENT"


def test_grade_level_must_be_known() -> None:
    app.dependency_overrides[get_lab_generator] = lambda: FakeGenerator()
    assert post(gradeLevel="Middle school").status_code == 422


# ------------------------------------------------- repairs found with the live model


def test_series_variable_that_is_also_a_control_becomes_a_meter() -> None:
    # gpt-4.1-mini did this for compound interest: t was both a slider and the time axis,
    # so the curve's marker silently overrode the slider.
    raw = load("mathematics")
    raw["visualMode"] = "curve"
    raw["series"] = {
        "variable": "t", "label": "Years", "unit": "yr", "min": 0, "max": 40,
        "steps": 120, "expression": raw["expression"], "markAt": 10,
    }
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.ok, result.problems
    assert result.level.visualMode == "meter"
    assert result.level.series is None
    f = output_function(result.level)
    constants = result.level.constants
    assert f({**constants, "r": 5, "t": 40}) > f({**constants, "r": 5, "t": 10})


def test_control_with_no_effect_is_rejected() -> None:
    raw = load("chemistry")
    raw["expression"] = "(n * R * 300) / P"  # temperature slider does nothing
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert not result.ok
    assert any("no effect" in p for p in result.problems)


def test_out_of_reach_target_widens_range_and_keeps_the_text_true() -> None:
    # gpt-4.1-mini capped temperature at 450 K, but 40 L at 100 kPa needs about 481 K.
    raw = load("chemistry")
    raw["controls"][1]["max"] = 450
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.ok
    stage = result.level.stages[1]
    assert stage.target.value == 40.0
    assert "40.0 L" in stage.challenge
    assert result.level.controls[1].max >= 481
    assert any("widened" in p for p in result.problems)


def test_clamped_target_rewrites_challenge_and_drops_stale_hints() -> None:
    raw = load("chemistry")
    raw["stages"][0]["target"]["value"] = 5000  # unreachable even after widening
    raw["stages"][0]["challenge"] = "Hold the temperature at 300 K. Compress the gas to 5000 L."
    raw["stages"][0]["hints"].append("You need exactly 5000 L.")
    result = validate_lab_level(LabLevel.model_validate(raw))
    stage = result.level.stages[0]
    assert "5000" not in stage.challenge
    assert f"{stage.target.value:,.1f}" in stage.challenge
    assert not any("5000" in h for h in stage.hints)


def test_single_notch_stage_is_loosened_when_the_change_is_modest() -> None:
    # gpt-4.1-mini gave college biology stages exactly one winning slider notch where a
    # second position was only 1.8x the tolerance away.
    raw = load("biology")
    raw["stages"][0]["target"]["tolerance"] = 3.0
    result = validate_lab_level(LabLevel.model_validate(raw))
    assert result.ok
    level, stage = result.level, result.level.stages[0]
    f = output_function(level)
    free = next(c for c in level.controls if c.key != stage.lock.key)
    count = int(round((free.max - free.min) / free.step)) + 1
    fixed = {**level.constants, stage.lock.key: stage.lock.value}
    outputs = [f({**fixed, free.key: free.min + k * free.step}) for k in range(count)]
    wins = sum(abs(o - stage.target.value) <= stage.target.tolerance for o in outputs)
    assert wins >= 2


def test_deliberate_single_answer_is_left_alone() -> None:
    # The handoff's compound-interest stage 2 has one winning rate (5.5%); the next
    # position misses by 3x the tolerance, so loosening would accept a wrong answer.
    result = validate_lab_level(LabLevel.model_validate(load("mathematics")))
    assert result.problems == []
    assert result.level.stages[1].target.tolerance == 80
