"""
Word Selector - Adaptive word selection based on difficulty level.
Selects words matching current difficulty preference while avoiding repetition.
"""

import random
from typing import Dict, List, Tuple, Any
from pathlib import Path

from utils.data_manager import read_json, reset_used_words, get_difficulty_level


def load_words(filepath: Path) -> List[Dict[str, Any]]:
    """
    Load words from JSON file.

    Args:
        filepath: Path to words JSON file

    Returns:
        List of word dictionaries
    """
    data = read_json(filepath)

    # Handle both 'verbs' and 'adjectives' keys
    if 'verbs' in data:
        return data['verbs']
    elif 'adjectives' in data:
        return data['adjectives']
    else:
        raise ValueError("Invalid word file format - missing 'verbs' or 'adjectives' key")


def filter_words_by_difficulty(
    words: List[Dict[str, Any]],
    target_difficulty: float,
    tolerance: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Filter words by difficulty level with tolerance.

    Args:
        words: List of all words
        target_difficulty: Target difficulty level (1.0-5.0)
        tolerance: How far from target to include (default 0.7)

    Returns:
        Filtered list of words within difficulty range
    """
    min_diff = max(1.0, target_difficulty - tolerance)
    max_diff = min(5.0, target_difficulty + tolerance)

    return [
        word for word in words
        if min_diff <= word.get('difficulty', 2.0) <= max_diff
    ]


def get_unused_words(
    all_words: List[Dict[str, Any]],
    used_ids: List[int]
) -> List[Dict[str, Any]]:
    """
    Filter out already used words.

    Args:
        all_words: List of all words
        used_ids: List of IDs that have been used

    Returns:
        List of unused words
    """
    return [word for word in all_words if word['id'] not in used_ids]


def select_word_by_difficulty_distribution(
    words: List[Dict[str, Any]],
    current_difficulty: float
) -> Dict[str, Any]:
    """
    Select a word using difficulty distribution:
    - 70% from current level (±0.5)
    - 20% from one level higher
    - 10% from one level lower

    Args:
        words: List of available words
        current_difficulty: Current difficulty level

    Returns:
        Selected word
    """
    if not words:
        raise ValueError("No words available to select from")

    # Define difficulty ranges
    current_range = filter_words_by_difficulty(words, current_difficulty, tolerance=0.5)
    higher_range = filter_words_by_difficulty(words, min(5.0, current_difficulty + 1.0), tolerance=0.5)
    lower_range = filter_words_by_difficulty(words, max(1.0, current_difficulty - 1.0), tolerance=0.5)

    # Randomly select which pool to use based on distribution
    rand = random.random()

    if rand < 0.70 and current_range:
        # 70%: Current level
        return random.choice(current_range)
    elif rand < 0.90 and higher_range:
        # 20%: Higher level (challenge)
        return random.choice(higher_range)
    elif rand < 1.00 and lower_range:
        # 10%: Lower level (review)
        return random.choice(lower_range)
    else:
        # Fallback: any available word
        return random.choice(words)


def select_daily_words(
    verbs_file: Path,
    adjectives_file: Path,
    history_file: Path
) -> Tuple[Dict[str, Any], Dict[str, Any], bool, bool]:
    """
    Select one verb and one adjective for daily email based on difficulty and usage history.

    Args:
        verbs_file: Path to verbs.json
        adjectives_file: Path to adjectives.json
        history_file: Path to history.json

    Returns:
        Tuple of (selected_verb, selected_adjective, verb_reset_occurred, adjective_reset_occurred)
    """
    # Load all words
    all_verbs = load_words(verbs_file)
    all_adjectives = load_words(adjectives_file)

    # Get history
    try:
        history = read_json(history_file)
        used_verbs = history.get('used_verbs', [])
        used_adjectives = history.get('used_adjectives', [])
        current_difficulty = history.get('current_difficulty_level', 2.0)
    except FileNotFoundError:
        used_verbs = []
        used_adjectives = []
        current_difficulty = 2.0

    # Get unused words
    unused_verbs = get_unused_words(all_verbs, used_verbs)
    unused_adjectives = get_unused_words(all_adjectives, used_adjectives)

    # Check if we need to reset (all words used)
    verb_reset = False
    adjective_reset = False

    if not unused_verbs:
        print("All verbs have been used! Resetting verb history...")
        reset_used_words(history_file, 'verbs')
        unused_verbs = all_verbs
        verb_reset = True

    if not unused_adjectives:
        print("All adjectives have been used! Resetting adjective history...")
        reset_used_words(history_file, 'adjectives')
        unused_adjectives = all_adjectives
        adjective_reset = True

    # Select words using difficulty distribution
    selected_verb = select_word_by_difficulty_distribution(unused_verbs, current_difficulty)
    selected_adjective = select_word_by_difficulty_distribution(unused_adjectives, current_difficulty)

    return selected_verb, selected_adjective, verb_reset, adjective_reset


def get_difficulty_name(level: float) -> str:
    """
    Convert difficulty level to human-readable name.

    Args:
        level: Difficulty level (1.0-5.0)

    Returns:
        Difficulty name string
    """
    if level < 1.5:
        return "Beginner"
    elif level < 2.5:
        return "Elementary"
    elif level < 3.5:
        return "Intermediate"
    elif level < 4.5:
        return "Advanced"
    else:
        return "Expert"


if __name__ == '__main__':
    # Test word selector
    from config.settings import Settings

    print("Testing word selector...")

    try:
        verb, adjective, v_reset, a_reset = select_daily_words(
            Settings.VERBS_FILE,
            Settings.ADJECTIVES_FILE,
            Settings.HISTORY_FILE
        )

        current_diff = get_difficulty_level(Settings.HISTORY_FILE)
        diff_name = get_difficulty_name(current_diff)

        print(f"\n✅ Selected words:")
        print(f"   Verb: {verb['spanish']} ({verb['english']}) - Difficulty: {verb['difficulty']}")
        print(f"   Adjective: {adjective['spanish_m']} ({adjective['english']}) - Difficulty: {adjective['difficulty']}")
        print(f"\n   Current difficulty level: {current_diff:.1f} ({diff_name})")

        if v_reset:
            print(f"   ⚠️  Verb list was reset (all verbs completed)")
        if a_reset:
            print(f"   ⚠️  Adjective list was reset (all adjectives completed)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
