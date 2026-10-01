import unittest

from src.freshness import (
    PredictionVoteBuffer,
    get_condition_group,
    select_priority_slot,
)


class FreshnessLogicTests(unittest.TestCase):
    def test_condition_normalization(self):
        cases = {
            "Tomato_rotten": "ROTTEN",
            "Tomato_intermediate_fresh": "RIPE",
            "Tomato_fresh": "FRESH",
            "ripe_apple": "RIPE",
            "unripe_apple": "FRESH",
            "rotten_apple": "ROTTEN",
        }
        for label, expected in cases.items():
            with self.subTest(label=label):
                self.assertEqual(get_condition_group(label), expected)

    def test_majority_vote(self):
        votes = PredictionVoteBuffer()
        votes.add("ripe_apple", 0.80)
        votes.add("ripe_apple", 0.70)
        votes.add("unripe_apple", 0.95)

        winner, confidence, winner_count, sample_count = votes.result()
        self.assertEqual(winner, "ripe_apple")
        self.assertAlmostEqual(confidence, 0.75)
        self.assertEqual(winner_count, 2)
        self.assertEqual(sample_count, 3)

    def test_priority_and_tie_break(self):
        slots = [
            {"slot": 1, "condition": "FRESH"},
            {"slot": 2, "condition": "RIPE"},
            {"slot": 3, "condition": "ROTTEN"},
            {"slot": 4, "condition": "ROTTEN"},
        ]
        self.assertEqual(select_priority_slot(slots)["slot"], 3)


if __name__ == "__main__":
    unittest.main()
