import time
import uuid
import cadence_flow
from cadence_flow.models import TaskPlan, Step

# 1. Define the original, successful plan
def create_greeting_plan(name: str) -> TaskPlan:
    return TaskPlan(
        plan_id=str(uuid.uuid4()),
        title=f"Greeting Plan for {name}",
        steps=[
            Step(id="s1_generate", description="Agent generates a creative greeting."),
            # The failing step has been removed.
            Step(id="s2_approve", description="Human approves the greeting.", ui_component="human_approval"),
            Step(id="s3_send", description="Send the approved greeting."),
        ]
    )

# 2. Define the executor for the successful path
def execute_step(step: Step, plan: TaskPlan) -> Step:
    print(f"EXECUTOR: Running step '{step.description}'...")
    if step.id == "s1_generate":
        time.sleep(2)
        step.result = {"greeting": f"Hello, World! Welcome, {plan.title.split(' for ')[-1]}."}
        step.status = "completed"
        
    elif step.id == "s3_send":
        # Check the result of the human approval step (s2_approve)
        approval_step = next((s for s in plan.steps if s.id == "s2_approve"), None)
        if approval_step and approval_step.result and approval_step.result.get("approved"):
            print("EXECUTOR: Greeting was approved. Pretending to send it!")
            step.status = "completed"
        else:
            print("EXECUTOR: Greeting was rejected. Aborting.")
            step.status = "failed"
            
    return step

if __name__ == "__main__":
    my_plan = create_greeting_plan("Alice")
    
    # Run the workflow
    final_plan = cadence_flow.run(plan=my_plan, executor_func=execute_step)
    
    print("\n--- Workflow Finished ---")
    print(final_plan.model_dump_json(indent=2))