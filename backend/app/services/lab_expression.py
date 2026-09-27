"""Safe evaluation of Relationship Lab formulas such as ``P * (1 + r / SCALE) ^ t``.

Expressions are parsed with ``ast`` and evaluated by walking the tree, never with
``eval``. ``^`` means exponentiation, as in textbook notation. Like the front end's
``evaluate.ts`` it is rewritten to ``**`` before parsing, which also gives it the right
precedence (Python's ``^`` binds looser than ``*``). The function set matches the front
end, so a formula that passes here also runs in the browser.
"""

import ast
import math
import operator
from collections.abc import Callable, Iterable

FUNCTIONS: dict[str, Callable[..., float]] = {
    "exp": math.exp,
    "log": math.log,
    "ln": math.log,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "abs": abs,
    "pow": math.pow,
    "min": min,
    "max": max,
    "floor": math.floor,
    "round": round,
}
CONSTANTS: dict[str, float] = {"PI": math.pi, "E": math.e}

BINARY_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

Compiled = Callable[[dict[str, float]], float]


class UnsafeExpressionError(ValueError):
    pass


def _check(node: ast.AST, names: set[str]) -> None:
    if isinstance(node, ast.Expression):
        _check(node.body, names)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise UnsafeExpressionError("only numeric literals are allowed")
    elif isinstance(node, ast.Name):
        if node.id not in names and node.id not in CONSTANTS:
            raise UnsafeExpressionError(f"unknown identifier: {node.id}")
    elif isinstance(node, ast.BinOp):
        if type(node.op) not in BINARY_OPS:
            raise UnsafeExpressionError("expression contains a disallowed operator")
        _check(node.left, names)
        _check(node.right, names)
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) not in UNARY_OPS:
            raise UnsafeExpressionError("expression contains a disallowed unary operator")
        _check(node.operand, names)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in FUNCTIONS:
            raise UnsafeExpressionError("expression contains a disallowed function")
        if node.keywords:
            raise UnsafeExpressionError("keyword arguments are not allowed")
        for arg in node.args:
            _check(arg, names)
    else:
        raise UnsafeExpressionError(f"unsupported expression element: {type(node).__name__}")


def _eval(node: ast.AST, scope: dict[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return float(node.value)
    if isinstance(node, ast.Name):
        return scope[node.id] if node.id in scope else CONSTANTS[node.id]
    if isinstance(node, ast.BinOp):
        return BINARY_OPS[type(node.op)](_eval(node.left, scope), _eval(node.right, scope))
    if isinstance(node, ast.UnaryOp):
        return UNARY_OPS[type(node.op)](_eval(node.operand, scope))
    if isinstance(node, ast.Call):
        return FUNCTIONS[node.func.id](*(_eval(arg, scope) for arg in node.args))  # type: ignore[union-attr]
    raise UnsafeExpressionError(f"unsupported expression element: {type(node).__name__}")


def compile_expression(expression: str, names: Iterable[str]) -> Compiled:
    """Parse and whitelist once; the returned function raises ValueError on non-finite results."""
    try:
        tree = ast.parse(expression.strip().replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        raise UnsafeExpressionError("expression is not valid mathematics") from exc
    _check(tree, set(names))

    def evaluate(scope: dict[str, float]) -> float:
        try:
            value = float(_eval(tree.body, scope))
        except (ArithmeticError, ValueError, TypeError, KeyError) as exc:
            raise ValueError("expression could not be evaluated") from exc
        if not math.isfinite(value):
            raise ValueError("expression did not produce a finite number")
        return value

    return evaluate
