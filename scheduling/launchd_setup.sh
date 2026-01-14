#!/bin/bash
# Setup script for macOS launchd scheduling
# This script installs and loads launchd agents for:
# 1. Daily email sending
# 2. Feedback checking (runs before daily email)

set -e  # Exit on error

echo "==============================================="
echo "🇪🇸 Spanish Email Bot - Launchd Setup"
echo "==============================================="

# Get project directory (parent of scheduling directory)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEDULING_DIR="$PROJECT_DIR/scheduling"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo ""
echo "Project directory: $PROJECT_DIR"
echo "LaunchAgents directory: $LAUNCH_AGENTS_DIR"

# Detect Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "❌ Error: python3 not found in PATH"
    exit 1
fi
echo "Python path: $PYTHON_PATH"

# Read send time from .env file
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "❌ Error: .env file not found. Please run setup.py first."
    exit 1
fi

SEND_TIME=$(grep "SEND_TIME=" "$PROJECT_DIR/.env" | cut -d'=' -f2)
if [ -z "$SEND_TIME" ]; then
    SEND_TIME="08:00"
    echo "⚠️  SEND_TIME not found in .env, using default: 08:00"
else
    echo "Send time from .env: $SEND_TIME"
fi

# Parse send time
SEND_HOUR=$(echo "$SEND_TIME" | cut -d':' -f1 | sed 's/^0*//')
SEND_MINUTE=$(echo "$SEND_TIME" | cut -d':' -f2 | sed 's/^0*//')

# Remove leading zeros (launchd doesn't like them)
SEND_HOUR=${SEND_HOUR:-0}
SEND_MINUTE=${SEND_MINUTE:-0}

# Feedback runs 5 minutes before daily email
FEEDBACK_HOUR=$SEND_HOUR
FEEDBACK_MINUTE=$((SEND_MINUTE - 5))
if [ $FEEDBACK_MINUTE -lt 0 ]; then
    FEEDBACK_MINUTE=$((FEEDBACK_MINUTE + 60))
    FEEDBACK_HOUR=$((FEEDBACK_HOUR - 1))
    if [ $FEEDBACK_HOUR -lt 0 ]; then
        FEEDBACK_HOUR=23
    fi
fi

echo ""
echo "Schedule:"
echo "  Feedback check: ${FEEDBACK_HOUR}:$(printf '%02d' $FEEDBACK_MINUTE)"
echo "  Daily email:    ${SEND_HOUR}:$(printf '%02d' $SEND_MINUTE)"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCH_AGENTS_DIR"

# Function to create plist from template
create_plist() {
    local template=$1
    local output=$2
    local hour=$3
    local minute=$4

    sed -e "s|{{PYTHON_PATH}}|$PYTHON_PATH|g" \
        -e "s|{{PROJECT_PATH}}|$PROJECT_DIR|g" \
        -e "s|{{SEND_HOUR}}|$hour|g" \
        -e "s|{{SEND_MINUTE}}|$minute|g" \
        -e "s|{{FEEDBACK_HOUR}}|$hour|g" \
        -e "s|{{FEEDBACK_MINUTE}}|$minute|g" \
        "$template" > "$output"

    echo "✅ Created: $output"
}

echo ""
echo "Creating plist files..."

# Create daily email plist
create_plist \
    "$SCHEDULING_DIR/com.spanish.daily.plist.template" \
    "$LAUNCH_AGENTS_DIR/com.spanish.daily.plist" \
    "$SEND_HOUR" \
    "$SEND_MINUTE"

# Create feedback plist
create_plist \
    "$SCHEDULING_DIR/com.spanish.feedback.plist.template" \
    "$LAUNCH_AGENTS_DIR/com.spanish.feedback.plist" \
    "$FEEDBACK_HOUR" \
    "$FEEDBACK_MINUTE"

echo ""
echo "Loading launchd agents..."

# Unload if already loaded (ignore errors)
launchctl unload "$LAUNCH_AGENTS_DIR/com.spanish.daily.plist" 2>/dev/null || true
launchctl unload "$LAUNCH_AGENTS_DIR/com.spanish.feedback.plist" 2>/dev/null || true

# Load agents
launchctl load "$LAUNCH_AGENTS_DIR/com.spanish.daily.plist"
echo "✅ Loaded: com.spanish.daily"

launchctl load "$LAUNCH_AGENTS_DIR/com.spanish.feedback.plist"
echo "✅ Loaded: com.spanish.feedback"

echo ""
echo "==============================================="
echo "✅ Setup Complete!"
echo "==============================================="
echo ""
echo "Your daily Spanish emails will be sent at ${SEND_HOUR}:$(printf '%02d' $SEND_MINUTE)"
echo "Feedback will be checked at ${FEEDBACK_HOUR}:$(printf '%02d' $FEEDBACK_MINUTE)"
echo ""
echo "Useful commands:"
echo "  Check status:    launchctl list | grep spanish"
echo "  Unload agents:   launchctl unload ~/Library/LaunchAgents/com.spanish.*.plist"
echo "  View logs:       tail -f $PROJECT_DIR/logs/*.log"
echo "  Manual trigger:  launchctl start com.spanish.daily"
echo ""
