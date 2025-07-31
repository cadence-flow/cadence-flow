import asyncio
import webbrowser
import uvicorn
import time
import threading
import traceback
from pathlib import Path
from typing import Callable

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .models import TaskPlan, Step
# Import the shared state and the websocket app
from . import state
from .websocket import app as sio_app, broadcast_plan

# --- FastAPI App Setup ---
app = FastAPI(title="Cadence Flow")
app.mount("/socket.io", sio_app)


# --- Core Asynchronous Execution Logic ---

# In cadence_flow/main.py

async def _run_async_flow(plan: TaskPlan, executor_func: Callable[[Step, TaskPlan], Step]):
    """The internal async function that executes the plan step-by-step."""
    print("INFO: Starting async execution flow.")
    
    await asyncio.sleep(1)
    await broadcast_plan(plan.model_dump())

    for i, step in enumerate(plan.steps):
        if step.status == "completed":
            continue

        print(f"--- Running Step: {step.description} ---")
        step.status = "running"
        await broadcast_plan(plan.model_dump())

        if step.ui_component == "human_approval":
            step.status = "waiting_for_human"
            state.human_input_event.clear()
            state.is_waiting_for_human_action = True
            
            await broadcast_plan(plan.model_dump())
            print(f"INFO: Waiting for human action for step: {step.id}")
            
            # --- THE CRITICAL CHANGE ---
            # Run the blocking wait() call in a thread pool to not freeze the asyncio loop
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, state.human_input_event.wait)
            # --- END OF CHANGE ---
            
            step.result = state.human_input_data.copy()
            step.status = "completed"
            print(f"INFO: Human action processed: {step.result}")
            await broadcast_plan(plan.model_dump())

        else: # Automated step
            try:
                loop = asyncio.get_event_loop()
                updated_step = await loop.run_in_executor(None, executor_func, step, plan)
                plan.steps[i] = updated_step
                await broadcast_plan(plan.model_dump())

                if updated_step.status == "failed":
                    print(f"ERROR: Step '{step.description}' failed. Halting workflow.")
                    break
            except Exception:
                print(f"ERROR: Unhandled exception in executor_func for step '{step.id}'. Halting workflow.")
                step.status = "failed"
                step.error = traceback.format_exc()
                plan.steps[i] = step
                await broadcast_plan(plan.model_dump())
                break
        
        print(f"INFO: Step '{step.id}' finished with status: {step.status}")

    print("\n--- Workflow Complete (or Halted) ---")
    state.is_waiting_for_human_action = False
    return plan

# --- Main User-Facing `run` Function ---

def run(
    plan: TaskPlan,
    executor_func: Callable[[Step, TaskPlan], Step],
    host: str = "127.0.0.1",
    port: int = 8501,
) -> TaskPlan:
    """The main entry point for running a Cadence workflow."""
    
    frontend_build_dir = Path(__file__).parent.parent / "frontend/build"
    if frontend_build_dir.exists():
        app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="static")
        print(f"INFO: Serving frontend from: {frontend_build_dir}")
    else:
        print(f"WARNING: Frontend build directory not found at {frontend_build_dir}.")

    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    url = f"http://{host}:{port}"
    plan.shareable_url = url
    webbrowser.open(url)
    
    final_plan = plan

    try:
        final_plan = asyncio.run(_run_async_flow(plan, executor_func))
    except KeyboardInterrupt:
        print("\nINFO: Keyboard interrupt received, shutting down.")
    finally:
        print("INFO: Allowing a moment for final UI updates...")
        time.sleep(1)
        print("INFO: Shutdown complete.")

    return final_plan