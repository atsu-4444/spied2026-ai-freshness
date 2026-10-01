from collections import Counter, defaultdict


FOOD_DISPLAY_NAMES = {
    "bell_pepper": "Bell Pepper",
    "carrot": "Carrot",
    "cucumber": "Cucumber",
    "potato": "Potato",
    "tomato": "Tomato",
    "apple": "Apple",
    "banana": "Banana",
    "mango": "Mango",
    "orange": "Orange",
    "strawberry": "Strawberry",
}

# Priority follows the SP!ED 2026 prototype concept:
# Rotten items should be checked first, then ripe/intermediate items,
# then fresh/unripe items.
PRIORITY_SCORE = {
    "UNKNOWN": 0,
    "FRESH": 1,
    "RIPE": 2,
    "ROTTEN": 3,
}


def normalize_label(label):
    if label is None:
        return ""
    return str(label).lower().replace("-", "_").replace(" ", "_")


def extract_food_name(label):
    normalized = normalize_label(label)

    if (
        "bell_pepper" in normalized
        or "bellpepper" in normalized
        or "bell__pepper" in normalized
    ):
        return "bell_pepper"

    for food in (
        "carrot",
        "cucumber",
        "potato",
        "tomato",
        "apple",
        "banana",
        "mango",
        "orange",
        "strawberry",
    ):
        if food in normalized:
            return food

    return None


def get_condition_group(label):
    """Normalize the model-specific labels into 3 priority groups.

    The checkpoint uses different terminology for different foods:
    - vegetables: fresh / intermediate_fresh / rotten
    - fruits: unripe / ripe / rotten

    For the portfolio demo, these are normalized to:
    FRESH < RIPE < ROTTEN for the priority decision.
    """
    normalized = normalize_label(label)
    if not normalized:
        return "UNKNOWN"

    if "rotten" in normalized:
        return "ROTTEN"
    if "intermediate_fresh" in normalized or "intermediate" in normalized:
        return "RIPE"
    if "ripe" in normalized and "unripe" not in normalized:
        return "RIPE"
    if "unripe" in normalized or "fresh" in normalized:
        return "FRESH"
    return "UNKNOWN"


def food_display_name(food_name):
    if food_name is None:
        return "Unknown"
    return FOOD_DISPLAY_NAMES.get(food_name, food_name.replace("_", " ").title())


def priority_score(condition):
    return PRIORITY_SCORE.get(condition, 0)


def select_priority_slot(slots):
    """Return the slot that should be checked first.

    Highest condition priority wins. When multiple slots have the same
    priority, the earlier slot number is selected to keep the behavior
    deterministic. Classification confidence is intentionally not used as a
    spoilage-severity score.
    """
    if not slots:
        return None

    valid = [slot for slot in slots if priority_score(slot.get("condition")) > 0]
    if not valid:
        return None

    return max(
        valid,
        key=lambda slot: (
            priority_score(slot.get("condition")),
            -int(slot.get("slot", 999)),
        ),
    )


class PredictionVoteBuffer:
    """Accumulate predictions during one manual slot scan.

    A scan runs for a fixed duration. The final class is selected by majority
    vote. If two labels have the same vote count, the label with the higher
    mean confidence wins.
    """

    def __init__(self):
        self.predictions = []

    def clear(self):
        self.predictions.clear()

    def add(self, label, confidence):
        self.predictions.append((str(label), float(confidence)))

    def result(self):
        if not self.predictions:
            return None, 0.0, 0, 0

        counts = Counter(label for label, _ in self.predictions)
        confidences = defaultdict(list)
        for label, confidence in self.predictions:
            confidences[label].append(confidence)

        winner = max(
            counts,
            key=lambda label: (
                counts[label],
                sum(confidences[label]) / len(confidences[label]),
            ),
        )
        winner_confidences = confidences[winner]
        avg_confidence = sum(winner_confidences) / len(winner_confidences)

        return (
            winner,
            avg_confidence,
            counts[winner],
            len(self.predictions),
        )
