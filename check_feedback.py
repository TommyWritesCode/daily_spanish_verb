#!/usr/bin/env python3
"""
Check for user feedback emails and update difficulty preferences.

This script checks Gmail inbox for replies to daily emails containing
feedback keywords like "easy", "hard", or "perfect" and adjusts the
difficulty level accordingly.

Usage:
    python3 check_feedback.py              # Check for feedback
    python3 check_feedback.py --days 7     # Check last 7 days
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings
from utils.feedback_processor import check_for_feedback


def setup_logging(log_file: Path, verbose: bool = False):
    """Configure logging to file and console."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_level = logging.DEBUG if verbose else logging.INFO

    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def main():
    """Main entry point for feedback checking."""
    parser = argparse.ArgumentParser(description='Check for feedback emails')
    parser.add_argument('--days', type=int, default=2, help='Number of days to check back (default: 2)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(Settings.LOG_FILE, args.verbose)

    logger.info("=" * 60)
    logger.info("Feedback Checker - Spanish Vocabulary Email Bot")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Validate configuration
        logger.info("Validating configuration...")
        Settings.validate()
        logger.info("✅ Configuration valid")

        # Check for feedback
        logger.info(f"\nChecking for feedback in the last {args.days} day(s)...")
        found, feedback_keyword, new_level = check_for_feedback(
            Settings.HISTORY_FILE,
            days_back=args.days
        )

        if found:
            logger.info(f"\n✅ Feedback found!")
            logger.info(f"   Keyword: '{feedback_keyword}'")
            logger.info(f"   New difficulty level: {new_level:.1f}")
            logger.info("\nThe next email will reflect this difficulty adjustment.")
            return 0
        else:
            logger.info("\nNo feedback found in recent emails.")
            logger.info("If you replied to a daily email, make sure:")
            logger.info("  - Your reply includes a keyword: easy, hard, or perfect")
            logger.info("  - You're replying from the recipient email address")
            logger.info(f"  - The email was sent within the last {args.days} day(s)")
            return 0

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
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
