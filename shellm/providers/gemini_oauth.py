"""
Gemini OAuth — Device Authorization Grant (RFC 8628).

This lets users log in with their Google account in a browser —
no API key needed. Works for Gemini free tier and Workspace accounts.

Flow:
  1. shellm requests a device code from Google
  2. User visits a short URL and enters the code (or we open the browser)
  3. shellm polls until the user approves
  4. shellm stores the access + refresh token in ~/.shellm/config.yaml
  5. On expiry, shellm silently refreshes using the refresh token

To use this in production you need to register shellm as a Google OAuth app
at console.cloud.google.com and set SHELLM_GOOGLE_CLIENT_ID /
SHELLM_GOOGLE_CLIENT_SECRET (or ship them as constants below once registered).
"""

import json
import os
import time
import urllib.request
import urllib.parse
import webbrowser

# ── Google OAuth constants ────────────────────────────────────────────────────
# Replace these with real values after registering shellm at:
# console.cloud.google.com → APIs & Services → Credentials → OAuth 2.0 Client IDs
# Application type: "TVs and Limited Input devices" (Device Auth Grant)
GOOGLE_CLIENT_ID     = os.environ.get("SHELLM_GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("SHELLM_GOOGLE_CLIENT_SECRET", "")

DEVICE_CODE_URL  = "https://oauth2.googleapis.com/device/code"
TOKEN_URL        = "https://oauth2.googleapis.com/token"
REVOKE_URL       = "https://oauth2.googleapis.com/revoke"
GEMINI_SCOPE     = "https://www.googleapis.com/auth/generative-language"


class GeminiOAuthError(Exception):
    pass


def _post(url: str, data: dict) -> dict:
    payload = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def login() -> dict:
    """
    Run the Device Authorization Grant flow.
    Returns token dict: {access_token, refresh_token, expires_at}.
    Raises GeminiOAuthError if client credentials are not configured.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise GeminiOAuthError(
            "Gemini OAuth is not yet configured.\n"
            "shellm needs a Google OAuth client registered at "
            "console.cloud.google.com.\n\n"
            "For now, use an API key instead:\n"
            "  shellm configure --provider gemini --api-key YOUR_KEY\n"
            "  (Free key at aistudio.google.com/apikey)"
        )

    # Step 1 — request device + user codes
    resp = _post(DEVICE_CODE_URL, {
        "client_id": GOOGLE_CLIENT_ID,
        "scope": GEMINI_SCOPE,
    })
    device_code      = resp["device_code"]
    user_code        = resp["user_code"]
    verification_url = resp["verification_url"]
    interval         = resp.get("interval", 5)
    expires_in       = resp.get("expires_in", 1800)

    # Step 2 — show user the URL + code, try to open browser
    print(f"\n🔐 Gemini login")
    print(f"   Open:  {verification_url}")
    print(f"   Enter: \033[1;33m{user_code}\033[0m")
    print(f"   (expires in {expires_in // 60} minutes)\n")
    try:
        webbrowser.open(verification_url)
        print("   Browser opened automatically ↑")
    except Exception:
        pass

    print("   Waiting for you to approve in the browser...", flush=True)

    # Step 3 — poll until approved or expired
    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token = _post(TOKEN_URL, {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            })
            if "access_token" in token:
                token["expires_at"] = int(time.time()) + token.get("expires_in", 3600)
                print("   ✅ Logged in to Google / Gemini\n")
                return token
            if token.get("error") == "access_denied":
                raise GeminiOAuthError("Login cancelled.")
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            if body.get("error") not in ("authorization_pending", "slow_down"):
                raise GeminiOAuthError(f"OAuth error: {body.get('error')}")
            if body.get("error") == "slow_down":
                interval += 5

    raise GeminiOAuthError("Login timed out — please try again.")


def refresh(token: dict) -> dict:
    """Refresh an expired access token using the stored refresh token."""
    new_token = _post(TOKEN_URL, {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": token["refresh_token"],
        "grant_type": "refresh_token",
    })
    new_token["refresh_token"] = token["refresh_token"]  # keep original
    new_token["expires_at"] = int(time.time()) + new_token.get("expires_in", 3600)
    return new_token


def is_expired(token: dict) -> bool:
    """Return True if the access token expires within 60 seconds."""
    return time.time() >= token.get("expires_at", 0) - 60


def revoke(token: dict) -> None:
    """Revoke the token (logout)."""
    _post(REVOKE_URL, {"token": token["access_token"]})
