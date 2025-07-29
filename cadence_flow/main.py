import uvicorn
import webbrowser
import threading
import asyncio
import traceback
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .models import TaskPlan, Step
from .websocket import app as sio_app, send_plan_update, human_input_event, human_input_data

# --- FastAPI App Setup ---
app = FastAPI()

# Mount the Socket.IO app
app.mount("/socket.io", sio_app)

# --- The Main `run` Function ---
def run_server_in_thread(shutdown_event):
    """Starts the Uvicorn server in a separate thread."""
    config = uvicorn.Config(app, host="127.0.0.1", port=8501, log_level="warning")
    server = uvicorn.Server(config)
    
    # Uvicorn doesn't have a simple graceful shutdown in this mode,
    # so we'll rely on the daemon thread for now. A more robust
    # solution would involve more complex process management.
    server.run()

def run(plan: TaskPlan, executor_func):
    """
    The main entry point for the Cadence library.
    It starts a server, opens a UI, and orchestrates the plan.
    """
    shutdown_event = threading.Event()
    server_thread = threading.Thread(target=run_server_in_thread, args=(shutdown_event,), daemon=True)
    server_thread.start()
    
    try:
        final_plan = asyncio.run(run_async(plan, executor_func))
    except KeyboardInterrupt:
        print("\nShutting down server.")
    
    shutdown_event.set()
    return final_plan

async def run_async(plan: TaskPlan, executor_func):
    """The async core of the execution logic."""
    plan.shareable_url = "http://127.0.0.1:8501"
    webbrowser.open(plan.shareable_url)
    
    await asyncio.sleep(2) # Give UI a moment to connect

    if not static_files_path.exists():
        print("WARNING: Frontend files not found. Please run `npm run build` in `frontend-src`.")
    
    await send_plan_update(plan.model_dump())

    for i, step in enumerate(plan.steps):
        if step.status == 'pending':
            # Handle automated steps
            if step.ui_component == 'none':
                step.status = 'running'
                await send_plan_update(plan.model_dump())
                
                try:
                    # Run the developer's code in a separate thread to avoid blocking
                    loop = asyncio.get_event_loop()
                    updated_step = await loop.run_in_executor(None, executor_func, step, plan)
                    plan.steps[i] = updated_step
                except Exception:
                    step.status = 'failed'
                    step.error = traceback.format_exc()
                
                await send_plan_update(plan.model_dump())

            # Handle human-in-the-loop steps
            elif step.ui_component == 'human_approval':
                step.status = 'waiting_for_human'
                await send_plan_update(plan.model_dump())
                
                human_input_event.clear()
                await human_input_event.wait()
                
                step.status = 'completed'
                step.result = human_input_data
                plan.steps[i] = step
                
                await send_plan_update(plan.model_dump())

    print("Workflow complete.")
    return plan

# This must be defined *after* the run_async function
static_files_path = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")