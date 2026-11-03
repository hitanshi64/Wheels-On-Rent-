"""
Small helper around the Razorpay REST API (https://razorpay.com/docs/api/).
Uses plain `requests`, so no extra SDK is needed.
All amounts passed to Razorpay are in PAISE (1 rupee = 100 paise).
"""
import hmac
import hashlib
import requests
from django.conf import settings

API_BASE = "https://api.razorpay.com/v1"
TIMEOUT = 20


class RazorpayError(Exception):
    pass


def _auth():
    return (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)


def _post(path, payload):
    try:
        resp = requests.post(f"{API_BASE}{path}", json=payload, auth=_auth(), timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise RazorpayError(f"Could not reach Razorpay: {exc}")
    try:
        data = resp.json()
    except ValueError:
        raise RazorpayError(f"Unexpected response from Razorpay (HTTP {resp.status_code})")
    if resp.status_code >= 400:
        message = data.get("error", {}).get("description", "Razorpay request failed")
        raise RazorpayError(message)
    return data


def to_paise(amount_rupees):
    return int(round(float(amount_rupees) * 100))


def create_order(amount_rupees, receipt):
    """Creates a Razorpay order and returns its JSON (contains 'id')."""
    return _post("/orders", {
        "amount": to_paise(amount_rupees),
        "currency": "INR",
        "receipt": str(receipt),
    })


def verify_payment_signature(order_id, payment_id, signature):
    """
    Razorpay signs 'order_id|payment_id' with your key secret (HMAC-SHA256).
    Returns True only if the signature is genuine.
    """
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{order_id}|{payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature or "")


def refund_payment(payment_id, amount_rupees, notes=None):
    """Refunds `amount_rupees` of a captured payment. Returns refund JSON (contains 'id')."""
    return _post(f"/payments/{payment_id}/refund", {
        "amount": to_paise(amount_rupees),
        "speed": "normal",
        "notes": notes or {},
    })
