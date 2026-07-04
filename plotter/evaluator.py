from typing import Optional

import numpy as np

DISCONTINUITY_MEDIAN_FACTOR = 20
DISCONTINUITY_RANGE_FACTOR = 0.5
LOWER_SCALE_PERCENTILE = 5
UPPER_SCALE_PERCENTILE = 95

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

        with np.errstate(all="ignore"):
            result = eval(formula, {"__builtins__": {}}, local_names)

        if np.isscalar(result):
            return float(result)

        if isinstance(result, np.ndarray):
            return result

        return None

    except Exception:
        return None


def prepare_y_values_for_plotting(
    y,
    expected_length: int | None = None,
) -> tuple[np.ndarray | None, str]:
    """
    Convert non-finite values and sharp jumps into plotting gaps.

    Returns:
        (prepared_values, "") if at least one finite value is available,
        (None, error_message) otherwise.
    """
    if y is None:
        return None, "Invalid formula."

    if not isinstance(y, np.ndarray):
        return None, "Formula must depend on x and return multiple y values."

    if y.ndim != 1:
        return None, "Formula returned an unsupported result shape."

    if expected_length is not None and len(y) != expected_length:
        return None, "Formula returned an unexpected number of values."

    try:
        prepared_y = np.asarray(y, dtype=float).copy()
    except (TypeError, ValueError):
        return None, "Formula returned unsupported non-numeric values."

    prepared_y[~np.isfinite(prepared_y)] = np.nan
    finite_mask = np.isfinite(prepared_y)

    if not finite_mask.any():
        return None, "Formula has no valid values in the selected x range."

    finite_y = prepared_y[finite_mask]
    if finite_y.size < 2:
        return prepared_y, ""

    lower_value, upper_value = np.percentile(
        finite_y,
        [LOWER_SCALE_PERCENTILE, UPPER_SCALE_PERCENTILE],
    )
    typical_y_range = upper_value - lower_value

    if typical_y_range == 0:
        return prepared_y, ""

    finite_pairs = finite_mask[:-1] & finite_mask[1:]
    differences = np.abs(np.diff(prepared_y))
    finite_differences = differences[finite_pairs]

    if finite_differences.size == 0:
        return prepared_y, ""

    median_difference = np.median(finite_differences)
    minimum_meaningful_difference = np.finfo(float).eps * max(1.0, typical_y_range)
    if median_difference <= minimum_meaningful_difference:
        return prepared_y, ""

    median_threshold = median_difference * DISCONTINUITY_MEDIAN_FACTOR
    range_threshold = typical_y_range * DISCONTINUITY_RANGE_FACTOR
    jump_indices = np.flatnonzero(
        finite_pairs
        & (differences > median_threshold)
        & (differences > range_threshold)
    )
    prepared_y[jump_indices + 1] = np.nan

    return prepared_y, ""


def validate_y_values(y, expected_length: int) -> tuple[bool, str]:
    """
    Validate calculated y values before plotting.

    Returns:
        (True, "") if values are valid,
        (False, error_message) if values are invalid.
    """
    prepared_y, error_message = prepare_y_values_for_plotting(
        y,
        expected_length=expected_length,
    )
    if prepared_y is None:
        return False, error_message

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
