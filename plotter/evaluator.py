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
