import unittest

import numpy as np

from plotter.evaluator import evaluate_formula


class EvaluateFormulaTests(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-10, 10, 201)

    def test_evaluates_array_formula(self):
        result = evaluate_formula("x**2", self.x)

        np.testing.assert_allclose(result, self.x**2)

    def test_broadcasts_scalar_result_to_x_shape(self):
        result = evaluate_formula("2", self.x)

        np.testing.assert_array_equal(result, np.full(self.x.shape, 2.0))

    def test_normalizes_infinity_to_nan(self):
        result = evaluate_formula("1/x", self.x)

        self.assertTrue(np.isnan(result[len(self.x) // 2]))
        self.assertFalse(np.isinf(result).any())

    def test_preserves_domain_nan_values(self):
        result = evaluate_formula("sqrt(x)", self.x)

        self.assertTrue(np.isnan(result[self.x < 0]).all())
        self.assertTrue(np.isfinite(result[self.x >= 0]).all())

    def test_rejects_invalid_formula(self):
        self.assertIsNone(evaluate_formula("not_a_function(x)", self.x))


if __name__ == "__main__":
    unittest.main()
