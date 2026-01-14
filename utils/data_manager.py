"""
Data Manager - Handles JSON file operations with atomic writes.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def read_json(filepath: Path) -> Dict[str, Any]:
    """
    Read and parse JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(filepath: Path, data: Dict[str, Any], pretty: bool = True) -> None:
    """
    Write data to JSON file with atomic write (write to temp, then rename).

    Args:
        filepath: Path to JSON file
        data: Data to write
        pretty: If True, format JSON with indentation
    """
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write to temporary file first
    fd, temp_path = tempfile.mkstemp(dir=filepath.parent, suffix='.json', text=True)

    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)

        # Atomic rename (on most systems)
        os.replace(temp_path, filepath)

    except Exception as e:
        # Clean up temp file if something went wrong
        try:
            os.unlink(temp_path)
        except:
            pass
        raise e


def update_history(
    history_file: Path,
    verb_id: int,
    adjective_id: int,
    success: bool,
    difficulty_level: float
) -> None:
    """
    Update history.json with new email sent data.

    Args:
        history_file: Path to history.json
        verb_id: ID of verb sent
        adjective_id: ID of adjective sent
        success: Whether email was sent successfully
        difficulty_level: Current difficulty level used
    """
    # Read current history
    try:
        history = read_json(history_file)
    except FileNotFoundError:
        # Initialize empty history if file doesn't exist
        history = {
            "sent_emails": [],
            "used_verbs": [],
            "used_adjectives": [],
            "total_emails_sent": 0,
            "current_difficulty_level": 2.0,
            "difficulty_adjustments": [],
            "last_feedback_check": None
        }

    # Add to sent emails
    history["sent_emails"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "verb_id": verb_id,
        "adjective_id": adjective_id,
        "success": success,
        "difficulty_level": difficulty_level
    })

    # Add to used words (only if successful)
    if success:
        if verb_id not in history["used_verbs"]:
            history["used_verbs"].append(verb_id)
        if adjective_id not in history["used_adjectives"]:
            history["used_adjectives"].append(adjective_id)

        history["total_emails_sent"] += 1

    # Write updated history
    write_json(history_file, history)


def reset_used_words(history_file: Path, word_type: str) -> None:
    """
    Reset used words list when all words have been sent.

    Args:
        history_file: Path to history.json
        word_type: Either 'verbs' or 'adjectives'
    """
    history = read_json(history_file)

    if word_type == 'verbs':
        history["used_verbs"] = []
    elif word_type == 'adjectives':
        history["used_adjectives"] = []
    else:
        raise ValueError(f"Invalid word_type: {word_type}. Must be 'verbs' or 'adjectives'")

    write_json(history_file, history)


def update_difficulty_preference(
    history_file: Path,
    feedback: str,
    adjustment: float
) -> float:
    """
    Update difficulty preference based on user feedback.

    Args:
        history_file: Path to history.json
        feedback: Feedback keyword (easy, hard, perfect)
        adjustment: Amount to adjust difficulty level

    Returns:
        New difficulty level
    """
    history = read_json(history_file)

    old_level = history.get("current_difficulty_level", 2.0)
    new_level = max(1.0, min(5.0, old_level + adjustment))  # Clamp between 1.0 and 5.0

    # Record the adjustment
    history["difficulty_adjustments"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "feedback": feedback,
        "old_level": old_level,
        "new_level": new_level
    })

    history["current_difficulty_level"] = new_level
    history["last_feedback_check"] = datetime.now().isoformat()

    write_json(history_file, history)

    return new_level


def get_difficulty_level(history_file: Path) -> float:
    """
    Get current difficulty level from history.

    Args:
        history_file: Path to history.json

    Returns:
        Current difficulty level (1.0-5.0)
    """
    try:
        history = read_json(history_file)
        return history.get("current_difficulty_level", 2.0)
    except FileNotFoundError:
        return 2.0  # Default to intermediate


if __name__ == '__main__':
    # Test data manager functions
    from config.settings import Settings

    print("Testing data manager...")

    # Test read functions
    try:
        verbs = read_json(Settings.VERBS_FILE)
        print(f"✅ Read {len(verbs['verbs'])} verbs")

        adjectives = read_json(Settings.ADJECTIVES_FILE)
        print(f"✅ Read {len(adjectives['adjectives'])} adjectives")

        history = read_json(Settings.HISTORY_FILE)
        print(f"✅ Read history (total emails: {history['total_emails_sent']})")

        # Test difficulty level
        level = get_difficulty_level(Settings.HISTORY_FILE)
        print(f"✅ Current difficulty level: {level}")

    except Exception as e:
        print(f"❌ Error: {e}")
