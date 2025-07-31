import asyncio
from typing import Dict, Any, List

import socketio

# --- Global objects for managing state and events ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# An asyncio.Event to signal when human input has been received
human_input_event = asyncio.Event()

# A global variable to store the data from the human input
human_input_data: Dict[str, Any] = {}

# --- NEW: State Cache for New Clients ---
# This variable will hold the most recent state of the TaskPlan.
# The underscore indicates it's for internal module use.
_last_plan_state: Dict[str, Any] | None = None


@sio.event
async def connect(sid: str, environ: dict):
    """
    Handles a new UI client connection.
    
    NEW BEHAVIOR: If a plan state has already been broadcast, immediately
    send the latest state to the newly connected client so their UI
    populates instantly.
    """
    print(f"UI Connected: {sid}")
    if _last_plan_state:
        print(f"INFO: Sending cached plan state to new client {sid}")
        # The 'to=sid' argument ensures this message goes ONLY to the new client.
        await sio.emit('plan_update', _last_plan_state, to=sid)

@sio.event
async def disconnect(sid: str):
    """Handles a client disconnection."""
    print(f"UI Disconnected: {sid}")

@sio.on('human_action')
async def handle_human_action(sid: str, data: dict):
    """
    Receives an action from the UI, stores the data,
    and sets the event to unblock the main execution loop.
    """
    global human_input_data
    print(f"Received human action: {data}")
    human_input_data = data
    human_input_event.set()

async def update_and_broadcast_plan(plan_data: dict):
    """
    NEW & IMPROVED: This function is the single point of truth for
    sending updates. It both updates our state cache and broadcasts
    the new state to all connected clients.
    """
    global _last_plan_state
    _last_plan_state = plan_data
    await sio.emit('plan_update', plan_data)
    print("INFO: Broadcasted plan_update to all clients.")