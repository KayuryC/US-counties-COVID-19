import unittest

import numpy as np
from pydantic import ValidationError

from backend.app import (
    MODEL_METRICS_CACHE,
    OVERVIEW_CACHE,
    PredictInput,
    predict,
)


class AppTest(unittest.TestCase):
    def test_prediction_uses_real_artifacts_and_normalized_probabilities(self):
        result = predict(
            PredictInput(
                month=6,
                day_of_week=1,
                new_cases=10,
                new_deaths=0,
                cfr=0.01,
            )
        )

        self.assertEqual(result["model_status"], "real_artifacts_loaded")
        for key in ["bayes", "logistic_regression", "decision_tree"]:
            probabilities = result[key]["probabilities"]
            self.assertTrue(np.isclose(sum(probabilities.values()), 1.0))

    def test_prediction_input_rejects_values_outside_domain(self):
        with self.assertRaises(ValidationError):
            PredictInput(
                month=13,
                day_of_week=7,
                new_cases=-1,
                new_deaths=-1,
                cfr=2,
            )

    def test_dashboard_payload_exposes_quality_and_model_metadata(self):
        self.assertEqual(OVERVIEW_CACHE["kpis"]["missing_deaths"], 57605)
        self.assertIn("daily_distributions", OVERVIEW_CACHE)
        self.assertEqual(
            set(MODEL_METRICS_CACHE["models"]),
            {"bayes", "logistic_regression", "decision_tree"},
        )


if __name__ == "__main__":
    unittest.main()
