"""Proves a generated Relationship Lab level is winnable before a student sees it.

Port of ``validateLevel`` in frontend/src/lib/games/lab/evaluate.ts. Sweep a grid over
both controls, then check every stage independently. A locked stage is swept only along
its free control, because that is all the student can move. Unreachable targets are
clamped into range; a stage still unsolvable after clamping is dropped. If nothing
survives, the level is rejected and the caller decides what to show instead.
"""

import math
import re
from dataclasses import dataclass, field

from app.models.lab import LabLevel
from app.services.lab_expression import Compiled, UnsafeExpressionError, compile_expression

GRID = 40
MAX_SLIDER_POSITIONS = 2000
MAX_FAILURE_SHARE = 0.2
# How far past its range a free control may be stretched to make the model's own target
# reachable, as fractions of the original span. Keeping the model's number keeps its
# challenge text and hints true.
WIDEN_STEPS = (0.25, 0.5, 1.0)
NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


@dataclass
class LabValidation:
    ok: bool
    level: LabLevel
    problems: list[str] = field(default_factory=list)


@dataclass
class Sweep:
    lo: float
    hi: float
    outputs: list[float]
    failures: int

    def nearest(self, value: float) -> float:
        return min((abs(o - value) for o in self.outputs), default=math.inf)


def _names(level: LabLevel) -> list[str]:
    names = [c.key for c in level.controls] + list(level.constants)
    if level.series:
        names.append(level.series.variable)
    return names


def output_function(level: LabLevel) -> Compiled:
    """Output for a pair of slider values: the series at its marker in curve mode."""
    names = _names(level)
    if level.visualMode == "curve" and level.series:
        series = level.series
        at = series.markAt if series.markAt is not None else series.max
        f = compile_expression(series.expression, names)
        return lambda scope: f({**scope, series.variable: at})
    return compile_expression(level.expression, names)


def _snap(value: float, lo: float, hi: float, step: float) -> float:
    value = min(max(value, lo), hi)
    return round(lo + round((value - lo) / step) * step, 10)


def _mentions(text: str, value: float) -> bool:
    return any(
        abs(float(m.group().replace(",", "")) - value) < 1e-9 for m in NUMBER.finditer(text)
    )


def _replace_number(text: str, old: float, new: str) -> str:
    return NUMBER.sub(
        lambda m: new if abs(float(m.group().replace(",", "")) - old) < 1e-9 else m.group(), text
    )


def validate_lab_level(level: LabLevel) -> LabValidation:
    level = level.model_copy(deep=True)
    problems: list[str] = []

    control_keys = {c.key for c in level.controls}
    if len(control_keys) != 2:
        return LabValidation(False, level, ["Controls must have two different keys"])
    if level.series and level.series.variable in control_keys:
        # The model made a slider the time axis too, so the curve's marker would override
        # the slider. What it meant is "the output at the slider's value": a meter.
        if level.visualMode == "curve":
            level.expression = level.series.expression
            level.visualMode = "meter"
            problems.append(
                f"Series variable {level.series.variable!r} is also a control; "
                "switched to meter mode so the slider drives the output"
            )
        level.series = None
    if level.visualMode == "curve" and level.series is None:
        return LabValidation(False, level, ["Curve mode requires a series"])

    empty = [c.key for c in level.controls if not c.max > c.min]
    if empty:
        return LabValidation(False, level, [f"Control {k} has an empty range" for k in empty])
    for c in level.controls:
        if not c.step > 0:
            c.step = (c.max - c.min) / 100
        if not c.min <= c.default <= c.max:
            c.default = (c.min + c.max) / 2

    try:
        f = output_function(level)
    except UnsafeExpressionError as exc:
        return LabValidation(False, level, [f"Unsafe expression: {exc}"])

    names = _names(level)
    safe_readouts = []
    for readout in level.readouts:
        try:
            compile_expression(readout.expression, names)
            safe_readouts.append(readout)
        except UnsafeExpressionError:
            problems.append(f"Readout {readout.label!r} had an unsafe expression, removed")
    level.readouts = safe_readouts

    a, b = level.controls

    def sweep(lock_key: str | None = None, lock_value: float = 0.0) -> Sweep:
        outputs: list[float] = []
        failures = 0
        def positions(c) -> list[float]:
            # A locked stage leaves one slider free: check every position the student can
            # actually reach. Otherwise (or for very fine sliders) sample a grid.
            count = math.floor((c.max - c.min) / c.step + 1e-9)
            if lock_key is not None and count <= MAX_SLIDER_POSITIONS:
                return [c.min + k * c.step for k in range(count + 1)]
            return [c.min + (c.max - c.min) * i / GRID for i in range(GRID + 1)]

        a_values = [lock_value] if lock_key == a.key else positions(a)
        b_values = [lock_value] if lock_key == b.key else positions(b)
        for va in a_values:
            for vb in b_values:
                try:
                    outputs.append(f({**level.constants, a.key: va, b.key: vb}))
                except ValueError:
                    failures += 1
        lo = min(outputs, default=math.inf)
        hi = max(outputs, default=-math.inf)
        return Sweep(lo, hi, outputs, failures)

    full = sweep()
    if full.failures > (GRID + 1) ** 2 * MAX_FAILURE_SHARE:
        return LabValidation(False, level, ["Expression failed across too much of the range"])

    for fixed, moving in ((b, a), (a, b)):
        s = sweep(fixed.key, fixed.default)
        if not s.hi - s.lo > 1e-9 * max(1.0, abs(s.hi)):
            return LabValidation(
                False, level, [*problems, f"Control {moving.key} has no effect on the output"]
            )

    def widen_to_reach(stage) -> str | None:
        """Stretch the stage's free control(s) until the target is reachable, if it helps."""
        free = [c for c in level.controls if not (stage.lock and stage.lock.key == c.key)]
        original = [(c.min, c.max) for c in free]
        for factor in WIDEN_STEPS:
            for c, (lo, hi) in zip(free, original, strict=True):
                span = hi - lo
                c.max = round(lo + math.ceil((hi + span * factor - lo) / c.step) * c.step, 10)
                if lo - span * factor > 0:
                    c.min = round(lo - math.floor(span * factor / c.step) * c.step, 10)
            s = sweep(stage.lock.key, stage.lock.value) if stage.lock else sweep()
            if s.failures == 0 and s.nearest(stage.target.value) <= stage.target.tolerance:
                return ", ".join(f"{c.key} to {c.min:g}-{c.max:g}" for c in free)
        for c, (lo, hi) in zip(free, original, strict=True):
            c.min, c.max = lo, hi
        return None

    if not level.output.max > level.output.min:
        level.output.min = min(0.0, full.lo)
        level.output.max = full.hi * 1.1
        problems.append("Output scale was invalid, derived from the reachable range")

    kept = []
    for n, stage in enumerate(level.stages, start=1):
        if stage.lock:
            control = next((c for c in level.controls if c.key == stage.lock.key), None)
            if control is None:
                problems.append(f"Stage {n} locks an unknown control, lock removed")
                stage.lock = None
            else:
                stage.lock.value = _snap(stage.lock.value, control.min, control.max, control.step)

        s = sweep(stage.lock.key, stage.lock.value) if stage.lock else full
        span = s.hi - s.lo
        if not math.isfinite(span) or span <= 0:
            problems.append(f"Stage {n} has no reachable range, dropped")
            continue

        target = stage.target
        if not target.tolerance > 0 or target.tolerance > span * 0.25:
            target.tolerance = max(span * 0.03, 1e-6)
            problems.append(f"Stage {n} tolerance was missing or too loose, tightened")

        if s.nearest(target.value) > target.tolerance:
            widened = widen_to_reach(stage)
            if widened:
                problems.append(f"Stage {n} target was out of reach, widened {widened}")
                full = sweep()
            else:
                old = target.value
                clamped = min(max(target.value, s.lo + span * 0.15), s.hi - span * 0.15)
                target.value = round(clamped, level.output.decimals)
                problems.append(f"Stage {n} target was unreachable, clamped into range")
                if s.nearest(target.value) > target.tolerance:
                    problems.append(f"Stage {n} still unsolvable after clamping, dropped")
                    continue
                # Keep the words true: the challenge names the new number, and hints that
                # quote the old one would now point at a losing answer.
                new = f"{target.value:,.{level.output.decimals}f}"
                stage.challenge = _replace_number(stage.challenge, old, new)
                stage.hints = [h for h in stage.hints if not _mentions(h, old)]

        if not stage.hints:
            stage.hints = ["Change one slider at a time and watch which way the result moves."]
        kept.append(stage)

    if not kept:
        return LabValidation(False, level, [*problems, "No stage survived validation"])

    level.stages = kept
    targets = [st.target.value for st in kept]
    if max(targets) > level.output.max or min(targets) < level.output.min:
        level.output.max = max(level.output.max, max(targets) * 1.2)
        level.output.min = min(level.output.min, min(targets))
        problems.append("Output scale did not cover every target, widened")
    if not level.completion:
        level.completion = "You worked through every challenge in this chapter."
    return LabValidation(True, level, problems)
