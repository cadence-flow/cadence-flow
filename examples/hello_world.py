# In examples/hello_world.py

import time
import uuid
import cadence_flow  # <-- CHANGED HERE
from cadence_flow.models import TaskPlan, Step # <-- AND HERE

def create_greeting_plan(name: str) -> TaskPlan:
    # Your latest model has plan_id, let's use it
    return TaskPlan(
        plan_id=str(uuid.uuid4()),
        title=f"Greeting Plan for {name}",
        steps=[
            Step(id="s1_generate", description="Agent generates a creative greeting."),
            Step(id="s2_approve", description="Human approves the greeting.", ui_component="human_approval"),
            Step(id="s3_send", description="Send the approved greeting."),
        ]
    )

def execute_step(step: Step, plan: TaskPlan) -> Step:
    # This logic remains the same
    print(f"EXECUTOR: Running step '{step.description}'...")
    if step.id == "s1_generate":
        time.sleep(2)
        step.result = {"greeting": f"Hello, World! Welcome, {plan.title.split(' for ')[-1]}."}
        step.status = "completed"
        print("EXECUTOR: Step completed.")
    elif step.id == "s3_send":
        approval_step = next((s for s in plan.steps if s.id == "s2_approve"), None)
        if approval_step and approval_step.result and approval_step.result.get("approved"):
            print("EXECUTOR: Greeting was approved. Pretending to send it!")
            step.status = "completed"
        else:
            print("EXECUTOR: Greeting was rejected. Skipping send.")
            step.result = {"reason": "Not approved by human."}
            step.status = "completed"
    return step

if __name__ == "__main__":
    print("--- Starting Cadence Hello World ---")
    my_plan = create_greeting_plan("Alice")
    
    # The magic function call also needs the new name
    final_plan = cadence_flow.run(plan=my_plan, executor_func=execute_step) # <-- CHANGED HERE
    
    print("\n--- Final Plan State ---")
    print(final_plan.model_dump_json(indent=2))