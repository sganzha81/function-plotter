import unittest

import numpy as np

from plotter.evaluator import evaluate_formula, prepare_y_values_for_plotting


class PrepareYValuesForPlottingTests(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-10, 10, 200)

    def prepare_formula(self, formula):
        y = evaluate_formula(formula, self.x)
        return prepare_y_values_for_plotting(y, expected_length=len(self.x))

    def test_rejects_non_array_results(self):
        prepared_y, error_message = prepare_y_values_for_plotting(1.0)

        self.assertIsNone(prepared_y)
        self.assertIn("depend on x", error_message)

    def test_rejects_formula_without_finite_values(self):
        prepared_y, error_message = self.prepare_formula("sqrt(-x**2 - 1)")

        self.assertIsNone(prepared_y)
        self.assertIn("no valid values", error_message)

    def test_preserves_valid_part_of_domain(self):
        for formula in ("sqrt(x)", "log(x)"):
            with self.subTest(formula=formula):
                prepared_y, error_message = self.prepare_formula(formula)

                self.assertEqual(error_message, "")
                self.assertTrue(np.isnan(prepared_y[self.x < 0]).all())
                self.assertTrue(np.isfinite(prepared_y[self.x > 0]).any())

    def test_inserts_gap_for_reciprocal_asymptote(self):
        prepared_y, error_message = self.prepare_formula("1/x")

        self.assertEqual(error_message, "")
        center = len(self.x) // 2
        self.assertTrue(np.isnan(prepared_y[center - 2 : center + 3]).any())
        self.assertTrue(np.isfinite(prepared_y[: center - 2]).any())
        self.assertTrue(np.isfinite(prepared_y[center + 3 :]).any())

    def test_inserts_gaps_for_tangent_asymptotes(self):
        prepared_y, error_message = self.prepare_formula("tan(x)")

        self.assertEqual(error_message, "")
        self.assertGreater(np.isnan(prepared_y).sum(), 1)
        self.assertTrue(np.isfinite(prepared_y).any())

    def test_does_not_modify_source_array(self):
        y = np.array([1.0, np.inf, 2.0])

        prepare_y_values_for_plotting(y)

        self.assertTrue(np.isinf(y[1]))


if __name__ == "__main__":
    unittest.main()
