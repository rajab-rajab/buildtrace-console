import unittest

from src.fallback_provider import FallbackProvider
from src.payload_validator import validate_payload


class FallbackProviderTests(unittest.TestCase):
    def test_template_has_a_valid_three_file_payload(self) -> None:
        payload = FallbackProvider().load()
        self.assertEqual(set(validate_payload(payload)), {"main.py", "database.py", "README.md"})


if __name__ == "__main__":
    unittest.main()
