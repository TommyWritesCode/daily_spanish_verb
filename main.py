#!/usr/bin/env python3
"""
Main script for sending daily Spanish vocabulary emails.

Usage:
    python3 main.py              # Send daily email
    python3 main.py --test       # Send test email
    python3 main.py --dry-run    # Select words without sending
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings
from utils.word_selector import select_daily_words, get_difficulty_name
from utils.email_sender import send_daily_email
from utils.data_manager import update_history, get_difficulty_level


def setup_logging(log_file: Path, verbose: bool = False):
    """
    Configure logging to file and console.

    Args:
        log_file: Path to log file
        verbose: If True, enable DEBUG level logging
    """
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    log_level = logging.DEBUG if verbose else logging.INFO

    # File handler with rotation
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def main():
    """Main entry point for the daily email bot."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Send daily Spanish vocabulary email')
    parser.add_argument('--test', action='store_true', help='Send test email')
    parser.add_argument('--dry-run', action='store_true', help='Select words without sending email')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(Settings.LOG_FILE, args.verbose)

    logger.info("=" * 60)
    logger.info("Daily Spanish Vocabulary Email Bot")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.test:
        logger.info("Running in TEST mode")
    elif args.dry_run:
        logger.info("Running in DRY RUN mode (no email will be sent)")

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Settings.validate()
        logger.info("✅ Configuration valid")

        # Select daily words
        logger.info("\nSelecting daily words...")
        verb, adjective, verb_reset, adj_reset = select_daily_words(
            Settings.VERBS_FILE,
            Settings.ADJECTIVES_FILE,
            Settings.HISTORY_FILE
        )

        # Get current difficulty
        current_difficulty = get_difficulty_level(Settings.HISTORY_FILE)
        difficulty_name = get_difficulty_name(current_difficulty)

        logger.info(f"\n📚 Selected Words:")
        logger.info(f"   Verb: {verb['spanish']} ({verb['english']})")
        logger.info(f"   - Conjugation: {verb['conjugation']}")
        logger.info(f"   - Example: {verb['example']}")
        logger.info(f"   - Difficulty: {verb.get('difficulty', 'N/A')}")
        logger.info(f"\n   Adjective: {adjective['spanish_m']}/{adjective['spanish_f']} ({adjective['english']})")
        logger.info(f"   - Forms: {adjective['plural_m']}, {adjective['plural_f']}")
        logger.info(f"   - Example: {adjective['example']}")
        logger.info(f"   - Difficulty: {adjective.get('difficulty', 'N/A')}")
        logger.info(f"\n   Current Difficulty: {current_difficulty:.1f} ({difficulty_name})")

        # Create reset message if needed
        reset_message = None
        if verb_reset or adj_reset:
            messages = []
            if verb_reset:
                messages.append("all verbs")
            if adj_reset:
                messages.append("all adjectives")

            reset_message = f'<div style="background-color: #fff3cd; padding: 12px; border-radius: 8px; margin: 16px 0; border-left: 4px solid #ffc107;">🎉 Congratulations! You\'ve completed {" and ".join(messages)}. Starting a new cycle!</div>'
            logger.info(f"\n🎉 Reset occurred: {', '.join(messages)}")

        # Dry run mode - skip sending
        if args.dry_run:
            logger.info("\n✅ Dry run complete - no email sent")
            return 0

        # Send email
        logger.info("\n📧 Sending email...")
        success = send_daily_email(
            verb,
            adjective,
            current_difficulty,
            difficulty_name,
            reset_message=reset_message,
            test_mode=args.test
        )

        if success:
            logger.info("✅ Email sent successfully!")

            # Update history
            logger.info("Updating history...")
            update_history(
                Settings.HISTORY_FILE,
                verb['id'],
                adjective['id'],
                success=True,
                difficulty_level=current_difficulty
            )
            logger.info("✅ History updated")

            return 0
        else:
            logger.error("❌ Failed to send email")
            return 1

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return 1
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    finally:
        logger.info(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)


if __name__ == '__main__':
    sys.exit(main())
