import httpx
from fastapi import FastAPI, HTTPException

from app.schemas import ChatRequest, SupportReply, TicketRequest, TicketResponse
from app.services import build_support, create_ticket

app = FastAPI(title="AI Customer Support Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=SupportReply)
def chat(body: ChatRequest):
    try:
        return build_support(body)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/tickets", response_model=TicketResponse)
def tickets(body: TicketRequest):
    try:
        return create_ticket(body)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="crm webhook failed") from exc
