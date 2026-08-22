import unittest

from my_info.model import load_pib_records


class MyInfoModelTests(unittest.TestCase):
    def test_loads_both_pib_scopes_with_unique_ids(self):
        records = load_pib_records()
        self.assertEqual(1028, len(records))
        self.assertEqual(1028, len({record.record_id for record in records}))
        self.assertEqual(49, sum(record.scope == "standard" for record in records))
        self.assertEqual(979, sum(record.scope == "institution" for record in records))

    def test_source_text_and_retention_are_normalized(self):
        records = {record.record_id: record for record in load_pib_records()}
        accounts_payable = records["standard:PSU 931"]
        self.assertIn("Accounts Payable", accounts_payable.text_en)
        self.assertIn("length of time", accounts_payable.retention_en)


if __name__ == "__main__":
    unittest.main()
