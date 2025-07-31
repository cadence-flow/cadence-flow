import asyncio
import webbrowser
import uvicorn
import os
import threading
import traceback
from pathlib import Path
from typing import Callable

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Use relative imports for modules within the same package
from .models import TaskPlan, Step
# --- CHANGED HERE: Import the new unified update function ---
from .websocket import app as sio_app, update_and_broadcast_plan, human_input_event, human_input_data

# --- FastAPI App Setup ---
app = FastAPI(
    title="Cadence Flow",
    description="The backend server for the Cadence human-in-the-loop UI."
)

# Mount the Socket.IO ASGI app at the conventional path
app.mount("/socket.io", sio_app)


# --- Core Asynchronous Execution Logic ---

async def _run_async_flow(plan: TaskPlan, executor_func: Callable[[Step, TaskPlan], Step]):
    """The internal async function that executes the plan step-by-step."""
    print("INFO: Starting async execution flow.")
    
    # Give the UI a moment to connect after the browser opens
    await asyncio.sleep(1)
    # --- CHANGED HERE: Use the new function name ---
    await update_and_broadcast_plan(plan.model_dump())

    for i, step in enumerate(plan.steps):
        # Skip steps that are already completed (e.g., in a resumed plan)
        if step.status == "completed":
            continue

        print(f"--- Running Step: {step.description} ---")
        step.status = "running"
        # --- CHANGED HERE: Use the new function name ---
        await update_and_broadcast_plan(plan.model_dump())

        # Check if this step requires human interaction
        if step.ui_component == "human_approval":
            step.status = "waiting_for_human"
            # --- CHANGED HERE: Use the new function name ---
            await update_and_broadcast_plan(plan.model_dump())
            print(f"INFO: Waiting for human action for step: {step.id}")

            human_input_event.clear()
            await human_input_event.wait()
            
            step.result = human_input_data.copy()
            step.status = "completed"
            print(f"INFO: Human action received: {step.result}")

        else: # This is an automated step
            try:
                # Run the user's potentially blocking code in a separate thread
                loop = asyncio.get_event_loop()
                updated_step = await loop.run_in_executor(None, executor_func, step, plan)
                plan.steps[i] = updated_step
                
                if updated_step.status == "failed":
                    print(f"ERROR: Step '{step.description}' failed. See details in plan.")
            
            except Exception:
                print(f"ERROR: Unhandled exception in executor_func for step '{step.id}'")
                step.status = "failed"
                step.error = traceback.format_exc()
                plan.steps[i] = step

        # --- CHANGED HERE: Use the new function name ---
        await update_and_broadcast_plan(plan.model_dump())
        print(f"INFO: Step '{step.id}' finished with status: {step.status}")

    print("\n--- Workflow Complete ---")
    return plan


# --- Main User-Facing `run` Function ---

def run(
    plan: TaskPlan,
    executor_func: Callable[[Step, TaskPlan], Step],
    host: str = "127.0.0.1",
    port: int = 8501,
) -> TaskPlan:
    """The main entry point for running a Cadence workflow."""
    
    # --- Mount Static Frontend Files ---
    frontend_build_dir = Path(__file__).parent.parent / "frontend/build"
    
    if frontend_build_dir.exists():
        app.mount("/", StaticFiles(directory=frontend_build_dir, html=True), name="static")
        print(f"INFO: Serving frontend from: {frontend_build_dir}")
    else:
        print(f"WARNING: Frontend build directory not found at {frontend_build_dir}. The UI will not be available. Please run `npm run build` in the 'frontend' directory.")

    # --- Start Server in a Separate Thread ---
    config = uvicorn.Config(app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # --- Open Browser and Run Workflow ---
    url = f"http://{host}:{port}"
    plan.shareable_url = url
    webbrowser.open(url)

    try:
        final_plan = asyncio.run(_run_async_flow(plan, executor_func))
    except KeyboardInterrupt:
        print("\nINFO: Keyboard interrupt received, shutting down.")
        return plan

    return final_plan