"""
Feedback Processor - Parse feedback emails and update difficulty preferences.
"""

import imaplib
import email
import re
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from pathlib import Path

from config.settings import Settings
from utils.data_manager import update_difficulty_preference, read_json


# Feedback keywords and their difficulty adjustments
FEEDBACK_KEYWORDS = {
    'easy': 0.5,
    'too easy': 0.5,
    'easier': 0.5,
    'simple': 0.5,
    'hard': -0.5,
    'too hard': -0.5,
    'harder': -0.5,
    'difficult': -0.5,
    'perfect': 0.0,
    'good': 0.0,
    'just right': 0.0,
}


def connect_imap() -> imaplib.IMAP4_SSL:
    """
    Connect to Gmail via IMAP.

    Returns:
        Authenticated IMAP connection
    """
    mail = imaplib.IMAP4_SSL(Settings.IMAP_SERVER, Settings.IMAP_PORT)
    mail.login(Settings.GMAIL_ADDRESS, Settings.GMAIL_APP_PASSWORD)
    return mail


def parse_feedback_from_text(text: str) -> Optional[str]:
    """
    Parse feedback keyword from email text.

    Args:
        text: Email body text

    Returns:
        Feedback keyword if found, None otherwise
    """
    # Convert to lowercase for matching
    text_lower = text.lower()

    # Check for feedback keywords
    for keyword in FEEDBACK_KEYWORDS.keys():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, text_lower):
            return keyword

    return None


def get_email_body(msg) -> str:
    """
    Extract text body from email message.

    Args:
        msg: Email message object

    Returns:
        Email body text
    """
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            pass

    return body


def check_for_feedback(
    history_file: Path,
    days_back: int = 2
) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Check Gmail inbox for feedback emails and process them.

    Args:
        history_file: Path to history.json
        days_back: How many days back to check for emails

    Returns:
        Tuple of (feedback_found, feedback_keyword, new_difficulty_level)
    """
    try:
        # Connect to Gmail
        mail = connect_imap()

        # Select inbox
        mail.select('INBOX')

        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

        # Search for emails from recipient (replies to our emails)
        # Search for emails that are replies (have "Re:" in subject)
        search_criteria = f'(FROM "{Settings.RECIPIENT_EMAIL}" SINCE {since_date})'
        _, message_numbers = mail.search(None, search_criteria)

        if not message_numbers[0]:
            mail.logout()
            return False, None, None

        # Get the most recent email
        latest_num = message_numbers[0].split()[-1]

        # Fetch the email
        _, msg_data = mail.fetch(latest_num, '(RFC822)')
        email_body = msg_data[0][1]
        msg = email.message_from_bytes(email_body)

        # Check if it's a reply to our daily email
        subject = msg.get('Subject', '')
        if 'daily spanish' not in subject.lower() and 're:' not in subject.lower():
            mail.logout()
            return False, None, None

        # Extract email body
        body = get_email_body(msg)

        # Parse feedback
        feedback = parse_feedback_from_text(body)

        mail.logout()

        if feedback:
            # Update difficulty preference
            adjustment = FEEDBACK_KEYWORDS[feedback]
            new_level = update_difficulty_preference(history_file, feedback, adjustment)

            print(f"✅ Feedback received: '{feedback}' (adjustment: {adjustment:+.1f})")
            print(f"   New difficulty level: {new_level:.1f}")

            return True, feedback, new_level
        else:
            return False, None, None

    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP error: {e}")
        return False, None, None
    except Exception as e:
        print(f"❌ Error checking feedback: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def get_feedback_adjustment_message(feedback: str, new_level: float) -> str:
    """
    Generate a friendly message about difficulty adjustment.

    Args:
        feedback: Feedback keyword received
        new_level: New difficulty level

    Returns:
        HTML formatted adjustment message
    """
    from utils.word_selector import get_difficulty_name

    difficulty_name = get_difficulty_name(new_level)

    if feedback in ['easy', 'too easy', 'easier', 'simple']:
        emoji = "📈"
        message = f"{emoji} I noticed you found the words too easy. "
        message += f"I've increased the difficulty to <strong>{difficulty_name} (Level {new_level:.1f})</strong>. "
        message += "Let me know if this is better!"
    elif feedback in ['hard', 'too hard', 'harder', 'difficult']:
        emoji = "📉"
        message = f"{emoji} I noticed you found the words too difficult. "
        message += f"I've decreased the difficulty to <strong>{difficulty_name} (Level {new_level:.1f})</strong>. "
        message += "Let me know if this is better!"
    elif feedback in ['perfect', 'good', 'just right']:
        emoji = "✅"
        message = f"{emoji} Great! I'll keep the difficulty at <strong>{difficulty_name} (Level {new_level:.1f})</strong>."
    else:
        return ""

    return f'<div style="background-color: #e3f2fd; padding: 12px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #2196f3;">{message}</div>'


if __name__ == '__main__':
    # Test feedback processor
    print("Testing feedback processor...")

    try:
        Settings.validate()

        print("Checking for feedback in the last 2 days...")
        found, feedback, new_level = check_for_feedback(Settings.HISTORY_FILE, days_back=2)

        if found:
            print(f"✅ Feedback found: {feedback}")
            print(f"   New difficulty level: {new_level:.1f}")

            # Generate adjustment message
            msg = get_feedback_adjustment_message(feedback, new_level)
            print(f"   Message: {msg[:100]}...")
        else:
            print("No feedback found in recent emails.")

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
