"""
Configuration settings loader for Spanish email bot.
Loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / '.env')


class Settings:
    """Configuration settings for the email bot"""

    # Gmail Configuration
    GMAIL_ADDRESS = os.getenv('GMAIL_ADDRESS')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

    # Email Settings
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
    SEND_TIME = os.getenv('SEND_TIME', '08:00')

    # File Paths (with defaults)
    VERBS_FILE = Path(os.getenv('VERBS_FILE', PROJECT_ROOT / 'data' / 'verbs.json'))
    ADJECTIVES_FILE = Path(os.getenv('ADJECTIVES_FILE', PROJECT_ROOT / 'data' / 'adjectives.json'))
    HISTORY_FILE = Path(os.getenv('HISTORY_FILE', PROJECT_ROOT / 'data' / 'history.json'))
    TEMPLATE_FILE = Path(os.getenv('TEMPLATE_FILE', PROJECT_ROOT / 'templates' / 'email_template.html'))
    LOG_FILE = Path(os.getenv('LOG_FILE', PROJECT_ROOT / 'logs' / 'email_bot.log'))

    # SMTP Configuration
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 465  # SSL

    # IMAP Configuration (for feedback checking)
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993

    @classmethod
    def validate(cls):
        """Validate required settings are present"""
        errors = []

        if not cls.GMAIL_ADDRESS:
            errors.append("GMAIL_ADDRESS not set in .env file")
        if not cls.GMAIL_APP_PASSWORD:
            errors.append("GMAIL_APP_PASSWORD not set in .env file")
        if not cls.RECIPIENT_EMAIL:
            errors.append("RECIPIENT_EMAIL not set in .env file")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    @classmethod
    def get_project_root(cls):
        """Return the project root directory"""
        return PROJECT_ROOT


if __name__ == '__main__':
    # Test configuration loading
    try:
        Settings.validate()
        print("✅ Configuration loaded successfully!")
        print(f"Gmail: {Settings.GMAIL_ADDRESS}")
        print(f"Recipient: {Settings.RECIPIENT_EMAIL}")
        print(f"Verbs file: {Settings.VERBS_FILE}")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
