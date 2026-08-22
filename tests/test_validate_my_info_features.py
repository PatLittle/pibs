import tempfile
import unittest
from pathlib import Path

from validate_my_info_features import _rows


class ValidateMyInfoFeaturesTests(unittest.TestCase):
    def test_csv_reader_preserves_utf8_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.csv"
            path.write_text("record_id,title_fr\na,Coordonnées\n", encoding="utf-8")
            self.assertEqual("Coordonnées", _rows(path)[0]["title_fr"])


if __name__ == "__main__":
    unittest.main()
