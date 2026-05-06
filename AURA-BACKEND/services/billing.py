"""Stripe billing service — checkout, webhook, portal."""
from __future__ import annotations

import logging
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

# Price IDs come from your Stripe dashboard — set these in .env
PRICE_PRO_MONTHLY  = os.getenv("STRIPE_PRICE_PRO_MONTHLY",  "price_pro_monthly_placeholder")
PRICE_TEAM_MONTHLY = os.getenv("STRIPE_PRICE_TEAM_MONTHLY", "price_team_monthly_placeholder")

TIER_PRICES = {
    "pro":  PRICE_PRO_MONTHLY,
    "team": PRICE_TEAM_MONTHLY,
}


@lru_cache(maxsize=1)
def _stripe():
    """Return a configured stripe module; raises RuntimeError if SDK not installed."""
    try:
        import stripe as _s
    except ImportError as exc:
        raise RuntimeError(
            "stripe SDK not installed. Run: pip install stripe==9.9.0"
        ) from exc
    api_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not api_key:
        raise RuntimeError("STRIPE_SECRET_KEY env var is not set")
    _s.api_key = api_key
    return _s


def create_checkout_session(tier: str, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout Session for *tier* ('pro' | 'team') and return its URL."""
    price_id = TIER_PRICES.get(tier)
    if not price_id:
        raise ValueError(f"Unknown tier: {tier!r}")

    stripe = _stripe()
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        allow_promotion_codes=True,
        billing_address_collection="auto",
    )
    logger.info("Checkout session created: %s (tier=%s)", session.id, tier)
    return session.url


def create_portal_session(customer_id: str, return_url: str) -> str:
    """Create a Stripe Customer Portal session and return its URL."""
    stripe = _stripe()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """Verify and parse a Stripe webhook event. Returns the event dict."""
    stripe = _stripe()
    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET env var is not set")

    event = stripe.Webhook.construct_event(payload, sig_header, secret)
    event_type: str = event["type"]
    logger.info("Stripe webhook received: %s", event_type)

    if event_type == "checkout.session.completed":
        _on_checkout_completed(event["data"]["object"])
    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        _on_subscription_changed(event["data"]["object"])

    return {"received": True}


def _on_checkout_completed(session: dict) -> None:
    """Stub — persist customer_id + tier to your user store here."""
    customer_id = session.get("customer")
    subscription_id = session.get("subscription")
    logger.info(
        "Checkout completed: customer=%s subscription=%s",
        customer_id, subscription_id,
    )
    # TODO: look up user by session metadata, set tier = "pro" | "team"


def _on_subscription_changed(subscription: dict) -> None:
    """Stub — update tier when subscription is cancelled or plan changes."""
    customer_id = subscription.get("customer")
    status = subscription.get("status")
    logger.info("Subscription changed: customer=%s status=%s", customer_id, status)
    # TODO: downgrade to free tier when status == "canceled"
