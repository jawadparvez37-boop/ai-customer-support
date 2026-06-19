import uuid

import httpx

from app.config import settings
from app.providers import generate
from app.schemas import ChatRequest, SupportReply, TicketRequest, TicketResponse


def build_support(body: ChatRequest) -> SupportReply:
    return generate(body.customer_id, body.message, body.provider)


def create_ticket(body: TicketRequest) -> TicketResponse:
    prompt = f"Subject: {body.subject}\n\n{body.message}"
    support = generate(body.customer_id, prompt, body.provider)
    ticket_id = f"T-{uuid.uuid4().hex[:10].upper()}"
    synced = push_to_crm(ticket_id, body, support)
    return TicketResponse(ticket_id=ticket_id, support=support, crm_synced=synced)


def push_to_crm(ticket_id: str, body: TicketRequest, support: SupportReply) -> bool:
    if not settings.crm_webhook_url:
        return False

    payload = {
        "ticket_id": ticket_id,
        "customer_id": body.customer_id,
        "subject": body.subject,
        "message": body.message,
        "category": support.category.value,
        "priority": support.priority.value,
        "needs_human": support.needs_human,
        "suggested_actions": support.suggested_actions,
    }

    headers = {"Content-Type": "application/json"}
    if settings.crm_webhook_token:
        headers["Authorization"] = f"Bearer {settings.crm_webhook_token}"

    with httpx.Client(timeout=10.0) as client:
        response = client.post(settings.crm_webhook_url, json=payload, headers=headers)
        response.raise_for_status()
    return True
