"""
Logging utilities for the verification game.

This module provides functions to log user choices and validation results
to a JSONL (JSON Lines) file for later analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


def log_verification_result(session_data: Dict[str, Any], round2_choice: str) -> None:
    """
    Log verification game results to a JSONL file.

    Creates the data directory and log file if they don't exist.
    Appends one JSON object per line for easy parsing.

    Args:
        session_data: Dictionary containing session information:
            - session_id: Unique session identifier
            - round1_passed: Boolean indicating if Round 1 was answered correctly
            - round1_data: Dictionary with Round 1 trick data and user selection
            - round2_data: Dictionary with Round 2 trick data
        round2_choice: User's selection in Round 2 ('left' or 'right')

    Log Entry Format:
        {
          "timestamp": "2025-12-31T10:30:45Z",
          "session_id": "uuid",
          "round1_passed": true/false,
          "round1_data": {
            "trick_left": {...},
            "trick_right": {...},
            "correct_position": "left"/"right",
            "user_selected": "left"/"right"
          },
          "round2_data": {
            "trick_left": {...},
            "trick_right": {...},
            "user_selected": "left"/"right"
          }
        }
    """
    # Get the log file path (relative to project root)
    project_root = Path(__file__).parent.parent.parent
    log_file = project_root / "data" / "verification_logs.jsonl"

    # Create data directory if it doesn't exist
    log_file.parent.mkdir(exist_ok=True)

    # Build log entry
    round1_data = session_data.get('round1_data', {})
    round2_data = session_data.get('round2_data', {})

    # Add user's Round 2 choice to round2_data
    round2_data['user_selected'] = round2_choice

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": session_data.get('session_id', 'unknown'),
        "round1_passed": session_data.get('round1_passed', False),
        "round1_data": round1_data,
        "round2_data": round2_data
    }

    # Append to JSONL file (one JSON object per line)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
