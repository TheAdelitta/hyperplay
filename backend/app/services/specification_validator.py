import ast

from app.models.simulation import SimulationSpec

ALLOWED_FUNCTIONS = {"sin", "cos", "tan", "sqrt", "abs", "min", "max"}
ALLOWED_CONSTANTS = {"pi"}
ALLOWED_BINARY_OPS = {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.BitXor}
ALLOWED_UNARY_OPS = {ast.UAdd, ast.USub}


class UnsafeExpressionError(ValueError):
    pass


def validate_expression(expression: str, variable_ids: set[str]) -> None:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise UnsafeExpressionError("expression is not valid mathematics") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and type(node.op) not in ALLOWED_BINARY_OPS:
            raise UnsafeExpressionError("expression contains a disallowed operator")
        if isinstance(node, ast.UnaryOp) and type(node.op) not in ALLOWED_UNARY_OPS:
            raise UnsafeExpressionError("expression contains a disallowed unary operator")
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCTIONS:
                raise UnsafeExpressionError("expression contains a disallowed function")
            if node.keywords:
                raise UnsafeExpressionError("keyword arguments are not allowed")
        if isinstance(node, ast.Name):
            if node.id.startswith("_"):
                raise UnsafeExpressionError("private identifiers are not allowed")
            if node.id not in variable_ids | ALLOWED_CONSTANTS | ALLOWED_FUNCTIONS:
                raise UnsafeExpressionError(f"unknown identifier: {node.id}")
        if isinstance(
            node,
            (
                ast.Attribute,
                ast.Subscript,
                ast.Lambda,
                ast.List,
                ast.Dict,
                ast.Set,
                ast.ListComp,
                ast.DictComp,
                ast.SetComp,
                ast.GeneratorExp,
                ast.NamedExpr,
            ),
        ):
            raise UnsafeExpressionError("expression contains disallowed syntax")
        if not isinstance(
            node,
            (
                ast.Expression,
                ast.BinOp,
                ast.UnaryOp,
                ast.Call,
                ast.Name,
                ast.Load,
                ast.Constant,
                ast.Add,
                ast.Sub,
                ast.Mult,
                ast.Div,
                ast.Mod,
                ast.Pow,
                ast.BitXor,
                ast.UAdd,
                ast.USub,
            ),
        ):
            raise UnsafeExpressionError(f"unsupported expression element: {type(node).__name__}")


def validate_specification(spec: SimulationSpec) -> SimulationSpec:
    variable_ids = {variable.id for variable in spec.variables}
    for metric in spec.metrics:
        validate_expression(metric.expression, variable_ids)
    return spec
