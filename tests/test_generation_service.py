import unittest

from src.generation_service import GenerationError, GenerationService


class FakeDelta:
    def __init__(self, content: str | None) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str | None) -> None:
        self.delta = FakeDelta(content)


class FakeChunk:
    def __init__(self, content: str | None) -> None:
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, result: object) -> None:
        self.result = result
        self.arguments: dict[str, object] | None = None

    def create(self, **kwargs: object) -> object:
        self.arguments = kwargs
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class FakeClient:
    def __init__(self, result: object) -> None:
        self.chat = type("Chat", (), {})()
        self.chat.completions = FakeCompletions(result)


class GenerationServiceTests(unittest.TestCase):
    def test_streams_json_mode_payload(self) -> None:
        chunks = [
            FakeChunk('{"database.py":"db",'),
            FakeChunk('"main.py":"main","README.md":"readme"}'),
        ]
        client = FakeClient(chunks)
        messages: list[str] = []
        payload = GenerationService(api_key="test-key", client=client).generate("Build it", messages.append)
        self.assertEqual(payload["main.py"], "main")
        arguments = client.chat.completions.arguments
        assert arguments is not None
        self.assertEqual(arguments["model"], "gpt-4o-mini")
        self.assertEqual(arguments["response_format"], {"type": "json_object"})
        self.assertTrue(arguments["stream"])
        self.assertTrue(any("Receiving" in message for message in messages))

    def test_wraps_api_failure_without_exposing_details(self) -> None:
        service = GenerationService(api_key="test-key", client=FakeClient(RuntimeError("sensitive transport detail")))
        with self.assertRaisesRegex(GenerationError, "RuntimeError"):
            service.generate("Build it", lambda _message: None)

    def test_rejects_missing_key(self) -> None:
        with self.assertRaises(GenerationError):
            GenerationService(api_key="").generate("Build it", lambda _message: None)


if __name__ == "__main__":
    unittest.main()
