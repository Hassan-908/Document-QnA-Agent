import ast
import operator as op

from langchain.tools import tool


OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _calculate(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numbers are allowed.")

    if isinstance(node, ast.UnaryOp):
        operator = OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError("Unsupported operator.")

        return operator(_calculate(node.operand))

    if isinstance(node, ast.BinOp):
        operator = OPERATORS.get(type(node.op))

        if operator is None:
            raise ValueError("Unsupported operator.")

        return operator(
            _calculate(node.left),
            _calculate(node.right),
        )

    raise ValueError("Invalid mathematical expression.")


@tool
def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression.
    Use this tool when an exact numerical calculation is required.
    """
    try:
        tree = ast.parse(expression, mode="eval")

        result = _calculate(tree.body)

        return str(result)

    except Exception as exc:
        return f"Could not calculate expression: {exc}"