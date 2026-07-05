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


def evaluate_formula(formula: str, x_val):
    try:
        local_names = {
            **ALLOWED_NAMES,
            "x": x_val,
        }

        with np.errstate(all="ignore"):
            result = eval(formula, {"__builtins__": {}}, local_names)

        result_array = np.asarray(result, dtype=float)
        x_array = np.asarray(x_val)
        if x_array.ndim > 0:
            if result_array.ndim == 0:
                result_array = np.full(x_array.shape, result_array, dtype=float)
            elif result_array.shape != x_array.shape:
                return None

        result_array = result_array.copy()
        result_array[np.isinf(result_array)] = np.nan
        return result_array
    except Exception:
        return None
