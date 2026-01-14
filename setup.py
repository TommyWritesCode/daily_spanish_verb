#!/usr/bin/env python3
"""
Interactive setup wizard for Spanish Email Bot.
Guides user through configuration and initialization.
"""

import os
import sys
import subprocess
from pathlib import Path
import re


def print_header():
    """Print welcome header."""
    print("\n" + "=" * 60)
    print("🇪🇸 Daily Spanish Vocabulary Email Bot - Setup")
    print("=" * 60)
    print("\nThis script will help you configure your email bot.")
    print("\nYou'll need:")
    print("  ✓ A Gmail account with 2FA enabled")
    print("  ✓ A Gmail App Password (I'll show you how to create one)")
    print("\nPress Enter to continue...")
    input()


def check_python_version():
    """Check Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_app_password(password: str) -> bool:
    """Validate Gmail App Password format (16 characters)."""
    # Remove spaces
    clean = password.replace(' ', '')
    # Should be 16 alphanumeric characters
    return len(clean) == 16 and clean.isalnum()


def validate_time(time_str: str) -> bool:
    """Validate time format (HH:MM)."""
    pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    return bool(re.match(pattern, time_str))


def get_input(prompt: str, validator=None, default=None) -> str:
    """
    Get user input with optional validation.

    Args:
        prompt: Prompt to display
        validator: Optional validation function
        default: Optional default value

    Returns:
        User input string
    """
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()

        if not user_input:
            print("❌ This field is required. Please try again.")
            continue

        if validator and not validator(user_input):
            print("❌ Invalid format. Please try again.")
            continue

        return user_input


def create_env_file(config: dict):
    """Create .env file from configuration."""
    project_root = Path(__file__).parent
    env_file = project_root / '.env'

    # Clean app password (remove spaces)
    app_password = config['app_password'].replace(' ', '')

    content = f"""# Gmail Configuration
GMAIL_ADDRESS={config['gmail_address']}
GMAIL_APP_PASSWORD={app_password}

# Email Settings
RECIPIENT_EMAIL={config['recipient_email']}
SEND_TIME={config['send_time']}

# Optional: Custom file paths (uses defaults if not specified)
# VERBS_FILE=data/verbs.json
# ADJECTIVES_FILE=data/adjectives.json
# HISTORY_FILE=data/history.json
# TEMPLATE_FILE=templates/email_template.html
# LOG_FILE=logs/email_bot.log
"""

    with open(env_file, 'w') as f:
        f.write(content)

    # Set restrictive permissions (owner read/write only)
    os.chmod(env_file, 0o600)

    print(f"✅ Created .env file with secure permissions (600)")


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    project_root = Path(__file__).parent
    requirements = project_root / 'requirements.txt'

    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements)],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("You can try manually: pip install -r requirements.txt")
        return False


def initialize_data_files():
    """Initialize data files and directories."""
    print("\n📁 Initializing data files...")
    project_root = Path(__file__).parent

    # Create logs directory
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    print("✅ Created logs directory")

    # Check history.json exists
    history_file = project_root / 'data' / 'history.json'
    if not history_file.exists():
        print("❌ Warning: history.json not found in data/ directory")
    else:
        print("✅ Data files verified")

    return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)

    print("\n📋 Next Steps:")
    print("\n1. Test the bot:")
    print("   python3 main.py --dry-run     # Select words without sending")
    print("   python3 main.py --test        # Send a test email")

    print("\n2. Set up daily scheduling:")
    print("   macOS:  ./scheduling/launchd_setup.sh")
    print("   Linux:  See scheduling/crontab_example.txt")

    print("\n3. Try the feedback system:")
    print("   - Reply to any daily email with 'easy', 'hard', or 'perfect'")
    print("   - Check feedback: python3 check_feedback.py")

    print("\n📚 Useful commands:")
    print("   python3 main.py               # Send daily email")
    print("   python3 check_feedback.py     # Check for feedback")
    print("   python3 main.py --verbose     # Run with debug logging")

    print("\n💡 Tip: Check logs/email_bot.log for detailed logs")
    print("\n" + "=" * 60 + "\n")


def main():
    """Main setup flow."""
    try:
        print_header()

        # Check Python version
        if not check_python_version():
            return 1

        print("\n" + "-" * 60)
        print("Configuration")
        print("-" * 60)

        # Collect configuration
        config = {}

        print("\n[1/4] Gmail sender address")
        config['gmail_address'] = get_input(
            "Enter your Gmail address",
            validator=validate_email
        )

        print("\n[2/4] Gmail App Password")
        print("ℹ️  You need to create an App Password:")
        print("    1. Go to: https://myaccount.google.com/apppasswords")
        print("    2. Select 'Mail' and generate a password")
        print("    3. Copy the 16-character password")
        config['app_password'] = get_input(
            "Enter your Gmail App Password (16 characters)",
            validator=validate_app_password
        )

        print("\n[3/4] Recipient email address")
        print("ℹ️  This is where daily emails will be sent (can be same as sender)")
        config['recipient_email'] = get_input(
            "Enter recipient email address",
            validator=validate_email,
            default=config['gmail_address']
        )

        print("\n[4/4] Send time")
        print("ℹ️  When should the daily email be sent? (24-hour format)")
        config['send_time'] = get_input(
            "Enter send time (HH:MM)",
            validator=validate_time,
            default="08:00"
        )

        # Create .env file
        print("\n" + "-" * 60)
        print("Creating configuration...")
        print("-" * 60)
        create_env_file(config)

        # Install dependencies
        if not install_dependencies():
            print("\n⚠️  Dependencies installation failed, but you can install them manually.")

        # Initialize data files
        initialize_data_files()

        # Print next steps
        print_next_steps()

        return 0

    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
