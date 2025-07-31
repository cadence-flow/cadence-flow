# In cadence_flow/websocket.py

import socketio

# Import the shared state objects
from . import state

# --- Socket.IO App Setup ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)


@sio.event
async def connect(sid: str, environ: dict):
    """Handles a new UI client connection and sends them the latest plan state."""
    print(f"UI Connected: {sid}")
    if state.last_plan_state:
        print(f"INFO: Sending cached plan state to new client {sid}")
        await sio.emit('plan_update', state.last_plan_state, to=sid)

@sio.event
async def disconnect(sid: str):
    """Handles a client disconnection."""
    print(f"UI Disconnected: {sid}")

@sio.on('human_action')
async def handle_human_action(sid: str, data: dict):
    """
    Receives an action from the UI and updates the shared state
    if the backend is actively waiting for it.
    """
    print(f"Received human action event from UI: {data}")
    
    if state.is_waiting_for_human_action:
        print("INFO: Backend is waiting, processing action.")
        state.is_waiting_for_human_action = False # Close the gate immediately
        state.human_input_data = data
        state.human_input_event.set()
    else:
        print("WARN: Received human_action while not waiting. Ignoring.")

async def broadcast_plan(plan_data: dict):
    """Updates the state cache and broadcasts the plan to all clients."""
    state.last_plan_state = plan_data
    await sio.emit('plan_update', plan_data)
    print("INFO: Broadcasted plan_update to all clients.")