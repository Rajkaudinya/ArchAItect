import sys
import types
import unittest
from unittest.mock import patch

from app.services import groq_search_client
from app.services import competitor_intelligence


class GroqSearchClientTests(unittest.TestCase):
    def test_extract_json_accepts_markdown_fence(self):
        result = groq_search_client._extract_json('```json\n{"competitor": "Netflix"}\n```')
        self.assertEqual(result["competitor"], "Netflix")

    def test_call_json_with_search_uses_compound_system(self):
        response = types.SimpleNamespace(choices=[
            types.SimpleNamespace(message=types.SimpleNamespace(
                content='{"competitor": "Netflix"}',
                executed_tools=[],
            ))
        ])
        create = unittest.mock.Mock(return_value=response)
        groq_constructor = unittest.mock.Mock(
            return_value=types.SimpleNamespace(
                chat=types.SimpleNamespace(
                    completions=types.SimpleNamespace(create=create)
                )
            )
        )
        fake_groq = types.SimpleNamespace(Groq=groq_constructor)

        with patch.object(groq_search_client.settings, "GROQ_API_KEY_3", "test-key"), \
             patch.dict(sys.modules, {"groq": fake_groq}):
            result = groq_search_client.call_json_with_search("system", "user")

        self.assertEqual(result["competitor"], "Netflix")
        self.assertEqual(
            groq_constructor.call_args.kwargs["default_headers"],
            {"Groq-Model-Version": "2025-07-23"},
        )
        self.assertEqual(create.call_args.kwargs["model"], "groq/compound-mini")
        self.assertNotIn("max_completion_tokens", create.call_args.kwargs)

    def test_retries_short_rate_limit_once(self):
        rate_limit = RuntimeError("rate limited")
        rate_limit.status_code = 429
        rate_limit.response = types.SimpleNamespace(headers={"retry-after": "2"})
        create = unittest.mock.Mock(side_effect=[
            rate_limit,
            types.SimpleNamespace(choices=[]),
        ])
        client = types.SimpleNamespace(
            chat=types.SimpleNamespace(
                completions=types.SimpleNamespace(create=create)
            )
        )

        with patch.object(groq_search_client.time, "sleep") as sleep:
            groq_search_client._create_completion_with_retry(client, "system", "user", 100)

        sleep.assert_called_once_with(2.0)
        self.assertEqual(create.call_count, 2)

    def test_drops_service_cards_without_search_result_url(self):
        data = {
            "known_services": [
                {"name": "Real", "source_hint": "Source https://example.com/real"},
                {"name": "Invented", "source_hint": "Source https://example.com/invented"},
            ]
        }

        result = groq_search_client._keep_grounded_services(data, {"https://example.com/real"})

        self.assertEqual([service["name"] for service in result["known_services"]], ["Real"])


class CompetitorIntelligenceTests(unittest.TestCase):
    def test_run_returns_fallback_when_research_fails(self):
        with patch.object(
            competitor_intelligence,
            "call_json_with_search",
            side_effect=RuntimeError("GROQ_API_KEY_3 is not configured"),
        ):
            result = competitor_intelligence.run("streaming", ["Video Service"])

        self.assertEqual(result["competitor"], "Unavailable")
        self.assertEqual(result["known_services"], [])
        self.assertIn("Add GROQ_API_KEY_3", result["why_relevant"])

    def test_run_returns_clear_rate_limit_message(self):
        rate_limit = RuntimeError("rate limited")
        rate_limit.status_code = 429
        with patch.object(
            competitor_intelligence,
            "call_json_with_search",
            side_effect=rate_limit,
        ):
            result = competitor_intelligence.run("streaming", ["Video Service"])

        self.assertIn("rate limit reached", result["why_relevant"])

    def test_run_returns_clear_payload_limit_message(self):
        payload_limit = RuntimeError("request too large")
        payload_limit.status_code = 413
        with patch.object(
            competitor_intelligence,
            "call_json_with_search",
            side_effect=payload_limit,
        ):
            result = competitor_intelligence.run("streaming", ["Video Service"])

        self.assertIn("lightweight Compound Mini", result["why_relevant"])


if __name__ == "__main__":
    unittest.main()
