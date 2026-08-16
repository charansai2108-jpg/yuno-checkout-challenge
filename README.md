# Yuno Demo — Run It Locally (Step by Step)

## What each file is
- `checkout.html` → the customer-facing page. Loads Yuno's SDK Full and
  renders the card form inline (no redirect).
- `app.py` → your Flask backend. Holds the SECRET key. Talks to Yuno's
  API to create the checkout session and process the payment.
- This README → setup instructions + demo notes.

You need BOTH running at once: the backend serves the API calls,
the HTML page is what you open in a browser.

---

## Step 1 — Install Python dependencies
Open a terminal in this folder and run:
```bash
pip install flask requests flask-cors --break-system-packages
```
(Drop `--break-system-packages` if you're on Windows or it errors.)

## Step 2 — Set your keys as environment variables
From the Yuno Dashboard → Developers → Authentication, copy your
Public key, Secret key, and Account code. Then in the SAME terminal:

**Mac/Linux:**
```bash
export YUNO_PUBLIC_API_KEY="paste_public_key"
export YUNO_PRIVATE_SECRET_KEY="paste_secret_key"
export YUNO_ACCOUNT_ID="a93370ae-8e93-4f52-a90b-08de09988f86"
```

**Windows (Command Prompt):**
```cmd
set YUNO_PUBLIC_API_KEY=paste_public_key
set YUNO_PRIVATE_SECRET_KEY=paste_secret_key
set YUNO_ACCOUNT_ID=a93370ae-8e93-4f52-a90b-08de09988f86
```

These only last for this terminal session — if you close the terminal,
redo this step before running `app.py` again.

## Step 3 — Run the backend
```bash
python3 app.py
```
Success looks like:
```
Running on http://127.0.0.1:5000
```
**Leave this terminal open** — this is your live backend. If it errors
instead, copy the exact error text (not your keys) and troubleshoot
from there.

## Step 4 — Put your public key into checkout.html
Open `checkout.html` in a text editor. Near the top of the `<script>`
tag, find:
```js
const YUNO_PUBLIC_API_KEY = "YOUR_PUBLIC_API_KEY";
```
Replace `"YOUR_PUBLIC_API_KEY"` with your real public key. Save.

## Step 5 — Open the checkout page
In a SECOND terminal window (keep the first one running app.py):
```bash
python3 -m http.server 8000
```
Then open your browser to:
```
http://localhost:8000/checkout.html
```
(Just double-clicking the file can work too, but some browsers block
local API calls that way — the http.server method is more reliable.)

## Step 6 — Test a payment
You should see the order summary and Yuno's card form load inline.
Enter a Yuno test card number (check Dashboard → Developers, or
search "Yuno test cards" in the docs for current sandbox numbers —
these change, so pull the live list rather than guessing) and submit.

Watch:
- The terminal running `app.py` — it'll show incoming requests.
- The status text below the form — SUCCEEDED / DECLINED.
- The Yuno Dashboard → Operations → Transactions — your test payment
  should appear there in real time.

---

## If something breaks
Send me the exact error message (from the terminal or browser console —
press F12 → Console tab in the browser) and I'll help you debug it.
Common first issues:
- 401/403 error → a key is wrong or wasn't exported before running `app.py`
- CORS error in browser console → backend isn't running, or wrong port
- Nothing renders in `#yuno-checkout` div → check browser console for
  a JS error loading the SDK script

## Demo talking points (for the actual call)
- **No redirect**: the SDK mounts inline in a `<div>` — point this out
  explicitly, it's requirement #2 from the brief.
- **Secret key isolation**: never touches the browser, lives in an env
  var on the backend only — ties to the doc's warning about not leaking
  secret keys on GitHub.
- **Idempotency key**: a fresh UUID per payment request, prevents
  double-charging on retry — mention this if asked about reliability.
- **Adding payment methods later**: dashboard config (Payment Methods →
  Connections → Routing), not new frontend code — requirement #3.
- **Routing you configured**: mention you built your own route
  (pointing Card traffic to the Test Payment Gateway connection) and
  that Yuno auto-archives the prior version on publish — shows you
  actually understand routing, not just clicked through it.
