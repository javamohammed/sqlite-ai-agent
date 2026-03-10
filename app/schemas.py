from typing import Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    result_type: str = "message"
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)