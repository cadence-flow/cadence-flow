# In cadence_flow/state.py

import threading  # <-- CHANGED FROM asyncio
from typing import Dict, Any

# This file holds the shared state for the application.

# --- Event and Data for Human Input ---
human_input_event = threading.Event()  # <-- THE CRITICAL CHANGE
human_input_data: Dict[str, Any] = {}

# --- State Machine Flag ---
is_waiting_for_human_action = False

# --- State Cache for New Clients ---
last_plan_state: Dict[str, Any] | None = None