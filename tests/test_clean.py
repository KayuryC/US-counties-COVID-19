import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.pipeline.clean import clean_dataset


class CleanDatasetTest(unittest.TestCase):
    def test_cleaning_preserves_missingness_and_observed_deaths(self):
        source = pd.DataFrame(
            [
                {
                    "date": "2024-01-01",
                    "county": "Alpha",
                    "state": "Test",
                    "fips": 1001,
                    "cases": 5,
                    "deaths": None,
                },
                {
                    "date": "2024-01-02",
                    "county": "Alpha",
                    "state": "Test",
                    "fips": 1001,
                    "cases": 2,
                    "deaths": 4,
                },
            ]
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            input_csv = Path(temp_dir) / "raw.csv"
            output_csv = Path(temp_dir) / "clean.csv"
            report = Path(temp_dir) / "report.md"
            source.to_csv(input_csv, index=False)

            clean_dataset(input_csv, output_csv, report)
            cleaned = pd.read_csv(output_csv)

        self.assertTrue(pd.isna(cleaned.loc[0, "deaths"]))
        self.assertEqual(cleaned.loc[1, "cases"], 4)
        self.assertEqual(cleaned.loc[1, "deaths"], 4)


if __name__ == "__main__":
    unittest.main()
