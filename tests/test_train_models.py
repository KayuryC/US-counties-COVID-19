import unittest

import numpy as np
import pandas as pd

from backend.pipeline.train_models import (
    calculate_class_priors,
    fit_manual_bayes,
    manual_bayes_log_posteriors,
    temporal_train_test_split,
)


class TrainModelsTest(unittest.TestCase):
    def test_priors_follow_observed_class_distribution(self):
        labels = np.array(["low", "low", "low", "medium", "high"])

        priors = calculate_class_priors(labels)

        np.testing.assert_allclose(priors, np.array([0.6, 0.2, 0.2]))

    def test_manual_bayes_uses_informed_priors(self):
        x_train = np.array(
            [
                [0.0],
                [0.2],
                [4.9],
                [5.1],
                [9.8],
                [10.0],
            ]
        )
        y_train = np.array(
            ["low", "low", "medium", "medium", "high", "high"]
        )
        priors = np.array([0.5, 0.3, 0.2])

        artifact = fit_manual_bayes(
            x_train, y_train, class_priors=priors
        )
        posteriors = manual_bayes_log_posteriors(
            np.array([5.0]), artifact
        )

        np.testing.assert_allclose(artifact["priors"], priors)
        self.assertEqual(artifact["classes"][int(np.argmax(posteriors))], "medium")

    def test_temporal_split_does_not_mix_dates(self):
        df = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]
                ),
                "risk_level": ["low", "medium", "high", "low"],
            }
        )

        train_df, test_df, cutoff = temporal_train_test_split(
            df, train_fraction=0.75
        )

        self.assertTrue((train_df["date"] < cutoff).all())
        self.assertTrue((test_df["date"] >= cutoff).all())
        self.assertLess(train_df["date"].max(), test_df["date"].min())


if __name__ == "__main__":
    unittest.main()
