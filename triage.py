from pydantic import BaseModel, field_validator
from pydantic_ai import Agent
import json
from config import SYSTEM_PROMPT, MODEL


class EmailClassification(BaseModel):
    id: str
    is_actionable: bool
    intent: str
    priority: str
    confidence: str
    requires_reply: bool
    deadline: str | None = None          
    reason: str                          
    suggested_action: str | None = None  
    
    @field_validator("intent", "priority", "confidence", mode="before")
    @classmethod
    def normalize(cls, v):
        return v.strip().lower() if isinstance(v, str) else v


class TriageResult(BaseModel):
    results: list[EmailClassification]


def agent_summary(inboxes: list[dict]) -> TriageResult:
    if not inboxes:
        return TriageResult(results=[])

    agent = Agent(
        model=MODEL,
        output_type=TriageResult,
        system_prompt=SYSTEM_PROMPT,
        model_settings={"temperature": 0},
    )
    
    print("thinking ...")
    response = agent.run_sync(
        "Classify these emails:\n" + json.dumps(inboxes, ensure_ascii=False),
    )

    return response.output
