import unittest

from src.payload_validator import PayloadValidationError, validate_payload


class PayloadValidatorTests(unittest.TestCase):
    def test_accepts_exact_expected_files(self) -> None:
        payload = {"main.py": "main", "database.py": "database", "README.md": "readme"}
        self.assertEqual(validate_payload(payload), payload)

    def test_rejects_missing_or_extra_files(self) -> None:
        with self.assertRaises(PayloadValidationError):
            validate_payload({"main.py": "main"})
        with self.assertRaises(PayloadValidationError):
            validate_payload({"main.py": "main", "database.py": "database", "README.md": "readme", "evil.py": "no"})


if __name__ == "__main__":
    unittest.main()
