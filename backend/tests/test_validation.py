import pytest

from app.services.fallback_generator import load_demo_spec
from app.services.specification_validator import UnsafeExpressionError, validate_expression


def test_demo_formulas_are_safe() -> None:
    spec = load_demo_spec()
    assert spec.id == "projectile-motion"


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('whoami')",
        "velocity.__class__",
        "unknown + velocity",
        "[velocity][0]",
        "lambda: velocity",
    ],
)
def test_rejects_unsafe_expressions(expression: str) -> None:
    with pytest.raises(UnsafeExpressionError):
        validate_expression(expression, {"velocity", "angle", "gravity"})


def test_accepts_math_expression() -> None:
    validate_expression(
        "(velocity^2 * sin(2 * angle * pi / 180)) / gravity",
        {"velocity", "angle", "gravity"},
    )
