import unittest

import numpy as np

from plotter.domain_engine import analyze_domain


class AnalyzeDomainTests(unittest.TestCase):
    def setUp(self):
        self.x = np.linspace(-10, 10, 201)

    def test_does_not_modify_inputs(self):
        y = self.x**2
        original_x = self.x.copy()
        original_y = y.copy()

        analyze_domain(self.x, y, "x**2")

        np.testing.assert_array_equal(self.x, original_x)
        np.testing.assert_array_equal(y, original_y)

    def test_reports_invalid_regions(self):
        y = np.where(self.x >= 0, np.sqrt(np.maximum(self.x, 0)), np.nan)

        signals = analyze_domain(self.x, y, "sqrt(x)")

        self.assertTrue(signals["invalid_regions"])
        self.assertEqual(signals["function_type"], "singular")

    def test_returns_required_signal_shapes(self):
        y = np.sin(self.x)

        signals = analyze_domain(self.x, y, "sin(x)")

        self.assertIsInstance(signals["discontinuities"], np.ndarray)
        self.assertIsInstance(signals["segment_breaks"], np.ndarray)
        self.assertEqual(signals["stability_map"].shape, y.shape)
        self.assertIn(
            signals["function_type"],
            {"continuous", "discontinuous", "periodic", "singular"},
        )

    def test_detects_asymptotic_segment_breaks_from_behavior(self):
        reciprocal_y = np.empty_like(self.x)
        np.divide(1, self.x, out=reciprocal_y, where=self.x != 0)
        reciprocal_y[self.x == 0] = np.nan

        for expression, y in (
            ("tan(x)", np.tan(self.x)),
            ("1/x", reciprocal_y),
        ):
            with self.subTest(expression=expression):
                signals = analyze_domain(self.x, y, expression)

                self.assertGreater(signals["segment_breaks"].size, 0)

    def test_smooth_signal_has_no_segment_breaks(self):
        signals = analyze_domain(self.x, np.sin(self.x), "sin(x)")

        self.assertEqual(signals["segment_breaks"].size, 0)


if __name__ == "__main__":
    unittest.main()
