from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any, Optional

class Step(BaseModel):
    id: str
    description: str
    status: Literal["pending", "running", "completed", "failed", "waiting_for_human"] = "pending"
    ui_component: Literal["none", "human_approval"] = "none"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class TaskPlan(BaseModel):
    plan_id: str
    title: str
    steps: List[Step]
    shareable_url: str = ""