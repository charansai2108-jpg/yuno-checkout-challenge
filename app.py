
"""
Yuno Technical Support Analyst Challenge — Backend
---------------------------------------------------
Minimal Flask backend that:
  1. Creates a Checkout Session (server-to-server, uses PRIVATE/SECRET key)
  2. Creates a Payment once the SDK returns a one-time token
  3. Talks to the Yuno TEST environment
 
HOW TO RUN (see README.md for full detail):
    pip install flask requests flask-cors --break-system-packages
 
    export YUNO_PUBLIC_API_KEY="your_public_key"
    export YUNO_PRIVATE_SECRET_KEY="your_secret_key"
    export YUNO_ACCOUNT_ID="a93370ae-8e93-4f52-a90b-08de09988f86"
 
    python3 app.py
"""
 
import os
import uuid
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
 
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)  # .env always wins over stale exported vars
except ImportError:
    pass  # dotenv is optional — you can still `export` vars manually
 
app = Flask(__name__)
CORS(app)  # allow checkout.html (served separately) to call this API
 
# --- Config: pulled from environment variables — never hardcode real keys ---
YUNO_PUBLIC_API_KEY = os.environ.get("YUNO_PUBLIC_API_KEY", "YOUR_PUBLIC_API_KEY")
YUNO_PRIVATE_SECRET_KEY = os.environ.get("YUNO_PRIVATE_SECRET_KEY", "YOUR_PRIVATE_SECRET_KEY")
YUNO_ACCOUNT_ID = os.environ.get("YUNO_ACCOUNT_ID", "YOUR_ACCOUNT_ID")
 
# Yuno's sandbox/test API base — confirm the exact host in docs.y.uno if calls 404
YUNO_API_BASE = "https://api-sandbox.y.uno/v1"
 
# Confirmed from docs.y.uno/reference/getting-started/authentication
BASE_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "public-api-key": YUNO_PUBLIC_API_KEY,
    "private-secret-key": YUNO_PRIVATE_SECRET_KEY,
}
 
 
def idempotency_header():
    """A fresh UUID per request, per Yuno's docs — prevents double-charging
    if a request is retried after a timeout."""
    return {"X-Idempotency-Key": str(uuid.uuid4())}
 
 
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """
    Called by the frontend BEFORE mounting the SDK.
    We create the customer + checkout session server-side so the secret
    key never touches the browser.
    """
    data = request.get_json(force=True)
 
    payload = {
        "account_id": YUNO_ACCOUNT_ID,
        "merchant_order_id": str(uuid.uuid4()),
        "amount": {
            "currency": data.get("currency", "USD"),
            "value": data.get("amount"),
        },
        "country": data.get("country", "US"),
        "customer": {
            "first_name": data["customer"]["first_name"],
            "last_name": data["customer"]["last_name"],
            "email": data["customer"]["email"],
        },
        "payment_description": "Yunique Fashion Store — Demo order",
    }
 
    resp = requests.post(
        f"{YUNO_API_BASE}/checkout/sessions",
        json=payload,
        headers={**BASE_HEADERS, **idempotency_header()},
        timeout=15,
    )
 
    if resp.status_code >= 400:
        return jsonify({"error": resp.text}), resp.status_code
 
    result = resp.json()
    return jsonify({"checkout_session": result.get("checkout_session")})
 
 
@app.route("/create-payment", methods=["POST"])
def create_payment():
    """
    Called by the frontend after the SDK produces a one-time token
    from the card the user entered. This is the step that actually
    moves money, so it always carries a fresh idempotency key.
    """
    data = request.get_json(force=True)
 
    payload = {
        "checkout": {"session": data["checkout_session"]},
        "payment_method": {
            "type": "CARD",
            "token": data["one_time_token"],
        },
        "description": "Yunique Fashion Store — Demo order",
    }
    if data.get("token_with_information"):
        payload["payment_method"]["token_with_information"] = data["token_with_information"]
 
    resp = requests.post(
        f"{YUNO_API_BASE}/payments",
        json=payload,
        headers={**BASE_HEADERS, **idempotency_header()},
        timeout=15,
    )
 
    if resp.status_code >= 400:
        return jsonify({"error": resp.text}), resp.status_code
 
    result = resp.json()
    return jsonify({
        "status": result.get("status"),
        "transaction_id": result.get("transaction_id") or result.get("id"),
        "sdk_action_required": result.get("sdk_action_required", False),
    })
 
 
if __name__ == "__main__":
    app.run(port=5000, debug=True)