import socketio
import asyncio

# --- Global objects for managing state and events ---
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# An asyncio.Event to signal when human input has been received
human_input_event = asyncio.Event()
# A global variable to store the data from the human input
human_input_data = {}
# A list to keep track of connected clients
connected_clients = []

@sio.event
async def connect(sid, environ):
    """Handles a new UI client connection."""
    print(f"UI Connected: {sid}")
    connected_clients.append(sid)

@sio.event
async def disconnect(sid):
    """Handles a client disconnection."""
    print(f"UI Disconnected: {sid}")
    connected_clients.remove(sid)

@sio.on('human_action')
async def handle_human_action(sid, data: dict):
    """
    Receives an action from the UI, stores the data,
    and sets the event to unblock the main execution loop.
    """
    global human_input_data
    print(f"Received human action: {data}")
    human_input_data = data
    human_input_event.set()

async def send_plan_update(plan_data: dict):
    """Broadcasts the entire plan state to all connected UIs."""
    if connected_clients:
        await sio.emit('plan_update', plan_data)