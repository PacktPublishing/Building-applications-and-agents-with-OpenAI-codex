"""A deliberately buggy four-operation calculator for the SandboxAgent lab."""


def add(left: float, right: float) -> float:
    return left + right


def subtract(left: float, right: float) -> float:
    return left - right


def multiply(left: float, right: float) -> float:
    # Intentional bug: this should multiply the operands.
    return left + right


def divide(left: float, right: float) -> float:
    return left / right
