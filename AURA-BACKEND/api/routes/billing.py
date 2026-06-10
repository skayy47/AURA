"""Billing routes — Stripe checkout, portal, webhook."""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["billing"])

_FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


class CheckoutRequest(BaseModel):
    tier: str  # "pro" | "team"
    locale: str = "en"


class PortalRequest(BaseModel):
    customer_id: str
    locale: str = "en"


@router.post("/billing/checkout")
async def create_checkout(body: CheckoutRequest):
    """Create a Stripe Checkout Session and return the redirect URL."""
    try:
        from services.billing import create_checkout_session
    except ImportError:
        raise HTTPException(503, detail="Billing service unavailable")

    success_url = f"{_FRONTEND_URL}/{body.locale}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{_FRONTEND_URL}/{body.locale}/billing/cancel"

    try:
        url = create_checkout_session(body.tier, success_url, cancel_url)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Checkout session creation failed")
        raise HTTPException(500, detail=str(exc)) from exc

    return {"url": url}


@router.post("/billing/portal")
async def customer_portal(body: PortalRequest):
    """Create a Stripe Customer Portal session and return the redirect URL."""
    try:
        from services.billing import create_portal_session
    except ImportError:
        raise HTTPException(503, detail="Billing service unavailable")

    return_url = f"{_FRONTEND_URL}/{body.locale}/account"

    try:
        url = create_portal_session(body.customer_id, return_url)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Portal session creation failed")
        raise HTTPException(500, detail=str(exc)) from exc

    return {"url": url}


@router.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """Receive Stripe webhook events."""
    try:
        from services.billing import handle_webhook
    except ImportError:
        raise HTTPException(503, detail="Billing service unavailable")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        result = handle_webhook(payload, sig_header)
    except RuntimeError as exc:
        raise HTTPException(503, detail=str(exc)) from exc
    except Exception as exc:
        logger.warning("Webhook handling error: %s", exc)
        raise HTTPException(400, detail="Webhook error") from exc

    return JSONResponse(result)
