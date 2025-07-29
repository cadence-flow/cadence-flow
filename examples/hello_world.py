import cadence as cd
import time

# A simple plan defined as a dictionary for ease of use
my_plan_dict = {
    "plan_id": "hello_world_001",
    "title": "Onboarding a New User",
    "steps": [
        {
            "id": "s1_create_user",
            "description": "System creates a new user account.",
            "ui_component": "none"
        },
        {
            "id": "s2_human_approval",
            "description": "Manager approves the new user's permissions.",
            "ui_component": "human_approval"
        },
        {
            "id": "s3_send_welcome",
            "description": "System sends a welcome email.",
            "ui_component": "none"
        }
    ]
}

def my_executor(step: cd.Step, plan: cd.TaskPlan) -> cd.Step:
    """A simple function to execute automated steps."""
    print(f"--- EXECUTING: {step.description} ---")
    time.sleep(2)  # Simulate I/O work like a database call or API request
    
    if step.id == "s1_create_user":
        step.result = {"user_id": "user_12345", "status": "created"}

    if step.id == "s3_send_welcome":
        step.result = {"email_status": "sent", "to": "new_user@example.com"}

    step.status = "completed"
    print(f"--- COMPLETED: {step.description} ---")
    return step

if __name__ == "__main__":
    # Cadence validates the dictionary into a Pydantic model internally
    my_plan = cd.TaskPlan(**my_plan_dict)
    
    final_plan_state = cd.run(
        plan=my_plan,
        executor_func=my_executor
    )

    print("\n--- WORKFLOW FINISHED ---")
    print("Final Plan State:")
    print(final_plan_state.model_dump_json(indent=2))

    # Example of using the final state
    approval_step = next(s for s in final_plan_state.steps if s.id == "s2_human_approval")
    if approval_step.result and approval_step.result.get('decision') == 'approved':
        print("\nACTION: User was approved. Welcome email sent.")
    else:
        print("\nACTION: User was rejected. No welcome email was sent.")