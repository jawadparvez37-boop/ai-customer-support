from enum import Enum

from pydantic import BaseModel, Field


class ProviderName(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Category(str, Enum):
    billing = "billing"
    shipping = "shipping"
    account = "account"
    product = "product"
    other = "other"


class ChatRequest(BaseModel):
    customer_id: str = Field(min_length=2, max_length=64)
    message: str = Field(min_length=3, max_length=4000)
    provider: ProviderName | None = None


class SupportReply(BaseModel):
    customer_id: str
    category: Category
    priority: Priority
    reply: str
    suggested_actions: list[str]
    needs_human: bool
    provider: ProviderName


class TicketRequest(BaseModel):
    customer_id: str
    subject: str = Field(min_length=3, max_length=200)
    message: str = Field(min_length=3, max_length=4000)
    provider: ProviderName | None = None


class TicketResponse(BaseModel):
    ticket_id: str
    support: SupportReply
    crm_synced: bool
