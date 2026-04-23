import unittest

from lotr_adventure.engine.commands import parse_command


class ParseCommandTests(unittest.TestCase):
    def test_parse_travel(self):
        parsed = parse_command("go to Bree")
        self.assertEqual(parsed.kind, "travel")
        self.assertEqual(parsed.target, "Bree")

    def test_parse_jump(self):
        parsed = parse_command("jump riddles")
        self.assertEqual(parsed.kind, "jump")
        self.assertEqual(parsed.target, "riddles")

    def test_parse_ask(self):
        parsed = parse_command("ask Gandalf about the ring")
        self.assertEqual(parsed.kind, "ask")
        self.assertEqual(parsed.target, "Gandalf")
        self.assertEqual(parsed.topic, "the ring")

    def test_parse_story_commands(self):
        self.assertEqual(parse_command("objective").kind, "objective")
        self.assertEqual(parse_command("hint").kind, "hint")
        self.assertEqual(parse_command("story").kind, "story_status")
        self.assertEqual(parse_command("continue").kind, "continue_story")
