from typing import Optional

import numpy as np

ALLOWED_NAMES = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "log": np.log,
    "exp": np.exp,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}


def evaluate_formula(formula: str, x_val) -> Optional[float | np.ndarray]:
    """
    Evaluate a mathematical formula for a given x value or numpy array.

    Returns:
        float or np.ndarray if formula is valid,
        None if formula is invalid.
    """
    try:
        local_names = {
            **ALLOWED_NAMES,
            "x": x_val,
        }

        result = eval(formula, {"__builtins__": {}}, local_names)

        if np.isscalar(result):
            return float(result)

        if isinstance(result, np.ndarray):
            return result

        return None

    except Exception:
        return None


def validate_y_values(y, expected_length: int) -> tuple[bool, str]:
    """
    Validate calculated y values before plotting.

    Returns:
        (True, "") if values are valid,
        (False, error_message) if values are invalid.
    """
    if y is None:
        return False, "Invalid formula."

    if np.isscalar(y):
        return False, "Formula must depend on x and return multiple y values."

    if not isinstance(y, np.ndarray):
        return False, "Formula returned an unsupported result type."

    if len(y) != expected_length:
        return False, "Formula returned an unexpected number of values."

    if np.isnan(y).any():
        return False, "Formula produced NaN values. Check the selected x range."

    if np.isinf(y).any():
        return False, "Formula produced infinite values. Check the selected x range."

    return True, ""


def validate_formula_at_points(formula: str, points: list[float]) -> tuple[bool, str]:
    """
    Validate formula at specific x points.

    This helps catch cases like 1/x when the plotting grid does not include x = 0.
    """
    for point in points:
        y = evaluate_formula(formula, point)

        if y is None:
            return False, f"Formula is invalid at x = {point}."

        if np.isnan(y):
            return False, f"Formula produced NaN at x = {point}."

        if np.isinf(y):
            return False, f"Formula produced infinity at x = {point}."

    return True, ""
