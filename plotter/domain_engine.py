import numpy as np


def _find_invalid_regions(x, invalid_mask):
    invalid_indices = np.flatnonzero(invalid_mask)
    if invalid_indices.size == 0:
        return []

    index_groups = np.split(
        invalid_indices,
        np.flatnonzero(np.diff(invalid_indices) > 1) + 1,
    )
    return [
        (float(x[indices[0]]), float(x[indices[-1]]))
        for indices in index_groups
    ]


def _is_periodic(y, finite_mask):
    if len(y) < 8 or not finite_mask.all():
        return False

    centered_y = y - np.mean(y)
    energy = np.dot(centered_y, centered_y)
    if energy <= np.finfo(float).eps:
        return False

    correlation = np.correlate(centered_y, centered_y, mode="full")
    correlation = correlation[len(y) - 1 :] / energy
    candidates = correlation[2 : len(y) // 2]
    if candidates.size < 3:
        return False

    peaks = (
        (candidates[1:-1] > candidates[:-2])
        & (candidates[1:-1] > candidates[2:])
        & (candidates[1:-1] > 0.5)
    )
    return bool(peaks.any())


def analyze_domain(x: np.ndarray, y: np.ndarray, expression: str):
    x_values = np.asarray(x, dtype=float)
    y_values = np.asarray(y, dtype=float)
    if x_values.ndim != 1 or y_values.ndim != 1:
        raise ValueError("x and y must be one-dimensional arrays")
    if x_values.shape != y_values.shape:
        raise ValueError("x and y must have matching shapes")

    finite_mask = np.isfinite(y_values)
    finite_pairs = finite_mask[:-1] & finite_mask[1:]
    differences = np.abs(np.diff(y_values))
    finite_differences = differences[finite_pairs]
    finite_magnitudes = np.abs(y_values[finite_mask])

    median_difference = (
        float(np.median(finite_differences))
        if finite_differences.size
        else 0.0
    )
    difference_scale = (
        float(np.percentile(finite_differences, 95))
        if finite_differences.size
        else 0.0
    )
    magnitude_scale = (
        float(np.percentile(finite_magnitudes, 95))
        if finite_magnitudes.size
        else 0.0
    )

    minimum_change = np.finfo(float).eps * max(1.0, magnitude_scale)
    large_gradient = max(median_difference * 20, minimum_change)
    extreme_gradient = max(median_difference * 50, minimum_change)

    discontinuity_mask = finite_pairs & (differences > large_gradient)
    discontinuities = np.flatnonzero(discontinuity_mask) + 1

    unstable_mask = finite_mask & (
        np.abs(y_values) > max(magnitude_scale * 5, np.finfo(float).eps)
    )
    invalid_mask = ~finite_mask | unstable_mask
    invalid_regions = _find_invalid_regions(x_values, invalid_mask)

    sign_changes = finite_pairs & (
        np.signbit(y_values[:-1]) != np.signbit(y_values[1:])
    )
    nonfinite_transitions = ~finite_pairs
    segment_break_mask = (
        nonfinite_transitions
        | (finite_pairs & (differences > extreme_gradient))
        | (sign_changes & (differences > large_gradient))
    )
    segment_breaks = np.flatnonzero(segment_break_mask) + 1

    normalized_magnitude = np.zeros_like(y_values, dtype=float)
    if magnitude_scale > 0:
        normalized_magnitude[finite_mask] = np.clip(
            np.abs(y_values[finite_mask]) / magnitude_scale,
            0,
            1,
        )

    normalized_difference = np.zeros_like(y_values, dtype=float)
    if difference_scale > 0:
        difference_indices = np.flatnonzero(finite_pairs) + 1
        normalized_difference[difference_indices] = np.clip(
            finite_differences / difference_scale,
            0,
            1,
        )

    stability_map = 1 - np.maximum(
        normalized_magnitude,
        normalized_difference,
    )
    stability_map[~finite_mask] = 0

    if invalid_regions or unstable_mask.any():
        function_type = "singular"
    elif discontinuities.size:
        function_type = "discontinuous"
    elif _is_periodic(y_values, finite_mask):
        function_type = "periodic"
    else:
        function_type = "continuous"

    return {
        "discontinuities": discontinuities,
        "invalid_regions": invalid_regions,
        "stability_map": stability_map,
        "segment_breaks": segment_breaks,
        "function_type": function_type,
    }
