import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import roundtable as rt


def response(content="A useful point.", finish="stop"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content), finish_reason=finish)],
        usage=SimpleNamespace(prompt_tokens=12, completion_tokens=8),
    )


class ConversationTests(unittest.TestCase):
    def setUp(self):
        self.people = [rt.Participant("A", "test/a", "Suggest."),
                       rt.Participant("B", "test/b", "Review.")]

    @patch("roundtable.completion_cost", return_value=0.001)
    @patch("roundtable.completion")
    def test_shared_history_across_rounds(self, complete, cost):
        complete.side_effect = [response(f"Reply {i}") for i in range(4)]
        turns = list(rt.generate_conversation("Testing", self.people, 2))
        self.assertEqual([t.speaker for t in turns], ["A", "B", "A", "B"])
        second = complete.call_args_list[1].kwargs["messages"][1]["content"]
        third = complete.call_args_list[2].kwargs["messages"][1]["content"]
        self.assertIn("A: Reply 0", second)
        self.assertIn("B: Reply 1", third)

    @patch("roundtable.completion")
    def test_missing_key_fails_before_any_call(self, complete):
        with patch.dict(os.environ, {}, clear=True):
            people = [self.people[0], rt.Participant("Cloud", "test/cloud", "Help.", "TEST_KEY")]
            with self.assertRaisesRegex(rt.ConversationError, "TEST_KEY"):
                list(rt.generate_conversation("Testing", people))
        complete.assert_not_called()

    def test_history_keeps_whole_turns(self):
        turns = [rt.Turn(1, "A", "a", "Old long reply"), rt.Turn(1, "B", "b", "Recent")]
        self.assertEqual(rt.recent_history(turns, max_chars=12), "B: Recent")

    @patch("roundtable.completion_cost", side_effect=ValueError("Unknown model"))
    @patch("roundtable.completion", return_value=response(finish="length"))
    def test_unknown_cost_and_truncation_are_visible(self, complete, cost):
        turns = list(rt.generate_conversation("Testing", self.people[:1]))
        self.assertIsNone(turns[0].cost_usd)
        self.assertIn("pricing unavailable", rt.usage_summary(turns))
        self.assertIn("incomplete", rt.transcript_markdown("Testing", turns))

    @patch("roundtable.completion", return_value=response(content=""))
    def test_empty_reasoning_reply_is_not_a_success(self, complete):
        with self.assertRaisesRegex(rt.ConversationError, "no visible text"):
            list(rt.generate_conversation("Testing", self.people))

    @patch("roundtable.completion_cost", return_value=0)
    @patch("roundtable.completion")
    def test_failure_preserves_prior_turn_and_hides_raw_error(self, complete, cost):
        complete.side_effect = [response("First reply"), RuntimeError("secret-key-should-not-appear")]
        conversation = rt.generate_conversation("Testing", self.people)
        self.assertEqual(next(conversation).content, "First reply")
        with self.assertRaises(rt.ConversationError) as caught:
            next(conversation)
        self.assertNotIn("secret-key", str(caught.exception))

    def test_sample_export_contains_only_conversation_data(self):
        topic, turns = rt.load_sample()
        self.assertEqual(len(turns), 4)
        with tempfile.TemporaryDirectory() as directory:
            path = rt.export_conversation(topic, turns, directory)
            with open(path) as handle:
                exported = json.load(handle)
        self.assertEqual(set(exported), {"topic", "turns"})
        self.assertEqual(exported["turns"][0]["content"], turns[0].content)


if __name__ == "__main__":
    unittest.main()
