import json

from openai import OpenAI
from anthropic import Anthropic

from app.config import settings
from app.schemas import ProviderName, SupportReply


def _schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["billing", "shipping", "account", "product", "other"],
            },
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "reply": {"type": "string"},
            "suggested_actions": {"type": "array", "items": {"type": "string"}},
            "needs_human": {"type": "boolean"},
        },
        "required": ["category", "priority", "reply", "suggested_actions", "needs_human"],
        "additionalProperties": False,
    }


def _system_prompt() -> str:
    return (
        "You are a customer support assistant. "
        "Return JSON only. Keep replies concise and actionable. "
        "Set needs_human=true for legal threats, chargebacks, or safety issues."
    )


def _parse_payload(raw: str, customer_id: str, provider: ProviderName) -> SupportReply:
    data = json.loads(raw)
    return SupportReply(customer_id=customer_id, provider=provider, **data)


def generate_openai(customer_id: str, message: str) -> SupportReply:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": message},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "support_reply", "schema": _schema()},
        },
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    return _parse_payload(content, customer_id, ProviderName.openai)


def generate_anthropic(customer_id: str, message: str) -> SupportReply:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=700,
        system=_system_prompt(),
        messages=[{"role": "user", "content": message}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return _parse_payload(text, customer_id, ProviderName.anthropic)


def generate(customer_id: str, message: str, provider: ProviderName | None) -> SupportReply:
    chosen = provider or ProviderName(settings.default_provider)
    if chosen == ProviderName.openai:
        return generate_openai(customer_id, message)
    return generate_anthropic(customer_id, message)
