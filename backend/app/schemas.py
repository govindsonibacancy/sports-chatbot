from typing import Any, Literal

from pydantic import BaseModel


class ChatRequirements(BaseModel):
    intent: Literal["product_search", "general_question", "unknown"] = "unknown"
    query: str | None = None
    sport: str | None = None
    category: str | None = None
    subcategory: str | None = None
    brand: str | None = None
    max_price: float | None = None
    user_skill_level: str | None = None


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    message: str
    requirements: ChatRequirements
    products: list[dict[str, Any]]
    total_matches: int
