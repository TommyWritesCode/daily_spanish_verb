"""
Email Sender - Handles Gmail SMTP connection and email sending.
"""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import Settings


def render_email_template(
    template_path: Path,
    verb: Dict[str, Any],
    adjective: Dict[str, Any],
    current_difficulty: float,
    difficulty_name: str,
    reset_message: Optional[str] = None,
    feedback_adjustment: Optional[str] = None
) -> str:
    """
    Render HTML email template with word data.

    Args:
        template_path: Path to HTML template file
        verb: Verb dictionary with all data
        adjective: Adjective dictionary with all data
        current_difficulty: Current difficulty level (1.0-5.0)
        difficulty_name: Human-readable difficulty name
        reset_message: Optional message if word lists were reset
        feedback_adjustment: Optional message about difficulty adjustment

    Returns:
        Rendered HTML string
    """
    # Read template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Get today's date
    from datetime import datetime
    today = datetime.now().strftime("%A, %B %d, %Y")

    # Replace template variables
    replacements = {
        '{{date}}': today,
        '{{verb_spanish}}': verb['spanish'],
        '{{verb_english}}': verb['english'],
        '{{verb_conjugation}}': verb['conjugation'],
        '{{verb_example}}': verb['example'],
        '{{verb_example_en}}': verb['example_en'],
        '{{adjective_spanish_m}}': adjective['spanish_m'],
        '{{adjective_spanish_f}}': adjective['spanish_f'],
        '{{adjective_plural_m}}': adjective['plural_m'],
        '{{adjective_plural_f}}': adjective['plural_f'],
        '{{adjective_english}}': adjective['english'],
        '{{adjective_example}}': adjective['example'],
        '{{adjective_example_en}}': adjective['example_en'],
        '{{difficulty_level}}': f"{current_difficulty:.1f}",
        '{{difficulty_name}}': difficulty_name,
        '{{reset_message}}': reset_message or '',
        '{{feedback_adjustment}}': feedback_adjustment or ''
    }

    for key, value in replacements.items():
        template = template.replace(key, str(value))

    return template


def create_smtp_connection(retries: int = 3, delay: int = 5) -> smtplib.SMTP_SSL:
    """
    Create and authenticate SMTP connection to Gmail with retry logic.

    Args:
        retries: Number of retry attempts
        delay: Delay between retries in seconds

    Returns:
        Authenticated SMTP connection

    Raises:
        smtplib.SMTPException: If connection or authentication fails
    """
    context = ssl.create_default_context()

    for attempt in range(retries):
        try:
            # Create SSL connection
            server = smtplib.SMTP_SSL(
                Settings.SMTP_SERVER,
                Settings.SMTP_PORT,
                context=context,
                timeout=30
            )

            # Authenticate
            server.login(Settings.GMAIL_ADDRESS, Settings.GMAIL_APP_PASSWORD)

            return server

        except (smtplib.SMTPException, OSError) as e:
            if attempt < retries - 1:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise


def send_email(
    smtp: smtplib.SMTP_SSL,
    from_addr: str,
    to_addr: str,
    subject: str,
    html_body: str
) -> bool:
    """
    Send HTML email via authenticated SMTP connection.

    Args:
        smtp: Authenticated SMTP connection
        from_addr: Sender email address
        to_addr: Recipient email address
        subject: Email subject
        html_body: HTML email body

    Returns:
        True if email was sent successfully

    Raises:
        smtplib.SMTPException: If email sending fails
    """
    # Create message
    message = MIMEMultipart('alternative')
    message['From'] = from_addr
    message['To'] = to_addr
    message['Subject'] = subject

    # Add HTML body
    html_part = MIMEText(html_body, 'html', 'utf-8')
    message.attach(html_part)

    # Send email
    smtp.send_message(message)

    return True


def send_daily_email(
    verb: Dict[str, Any],
    adjective: Dict[str, Any],
    current_difficulty: float,
    difficulty_name: str,
    reset_message: Optional[str] = None,
    feedback_adjustment: Optional[str] = None,
    test_mode: bool = False
) -> bool:
    """
    Send daily Spanish vocabulary email.

    Args:
        verb: Verb data
        adjective: Adjective data
        current_difficulty: Current difficulty level
        difficulty_name: Human-readable difficulty name
        reset_message: Optional reset notification
        feedback_adjustment: Optional feedback adjustment message
        test_mode: If True, use test recipient

    Returns:
        True if email was sent successfully
    """
    try:
        # Render email template
        html_body = render_email_template(
            Settings.TEMPLATE_FILE,
            verb,
            adjective,
            current_difficulty,
            difficulty_name,
            reset_message,
            feedback_adjustment
        )

        # Create SMTP connection
        smtp = create_smtp_connection()

        # Send email
        subject = "🇪🇸 Your Daily Spanish Vocabulary"
        recipient = Settings.RECIPIENT_EMAIL

        print(f"Sending email to {recipient}...")

        send_email(
            smtp,
            Settings.GMAIL_ADDRESS,
            recipient,
            subject,
            html_body
        )

        # Close connection
        smtp.quit()

        print(f"✅ Email sent successfully to {recipient}")
        return True

    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test email sending (requires .env to be configured)
    print("Testing email sender...")

    # Create test data
    test_verb = {
        'spanish': 'hablar',
        'english': 'to speak',
        'conjugation': 'hablo, hablas, habla, hablamos, habláis, hablan',
        'example': 'Yo hablo español todos los días.',
        'example_en': 'I speak Spanish every day.'
    }

    test_adjective = {
        'spanish_m': 'rojo',
        'spanish_f': 'roja',
        'plural_m': 'rojos',
        'plural_f': 'rojas',
        'english': 'red',
        'example': 'El coche rojo es muy rápido.',
        'example_en': 'The red car is very fast.'
    }

    try:
        Settings.validate()
        print("Configuration valid, but not sending test email.")
        print("Run main.py --test to send a test email.")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please create a .env file with your credentials.")
