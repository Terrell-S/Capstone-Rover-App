"""Simple Firebase Authentication helpers using the REST API.

This module avoids adding third-party deps and uses urllib.request
to POST JSON to the Identity Toolkit endpoints.

Functions:
 - sign_in_with_email_and_password(api_key, email, password)
 - sign_up_with_email_and_password(api_key, email, password)

Returns the parsed JSON response on success or raises a RuntimeError with
the error message on failure.
"""
from __future__ import annotations

import json
from typing import Dict
import urllib.request
import urllib.error


BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def _post(endpoint: str, api_key: str, payload: Dict) -> Dict:
    url = f"{BASE_URL}:{endpoint}?key={api_key}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            return json.loads(body.decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
            err = json.loads(body.decode("utf-8"))
            # Firebase returns error details in this shape
            msg = err.get("error", {}).get("message", str(err))
        except Exception:
            msg = e.reason
        raise RuntimeError(f"Firebase error: {msg}")
    except Exception as e:
        raise RuntimeError(f"Network error: {e}")


def sign_in_with_email_and_password(api_key: str, email: str, password: str) -> Dict:
    """
    Sign in an existing user with email/password.

    Returns the response dict which contains idToken, refreshToken, localId, expiresIn, etc.
    Raises RuntimeError on failure.
    """
    if not api_key:
        raise RuntimeError("Missing Firebase API key")
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return _post("signInWithPassword", api_key, payload)


def sign_up_with_email_and_password(api_key: str, email: str, password: str) -> Dict:
    """
    Create a new user account with email/password.

    Returns the response dict on success or raises RuntimeError.
    """
    if not api_key:
        raise RuntimeError("Missing Firebase API key")
    payload = {"email": email, "password": password, "returnSecureToken": True}
    return _post("signUp", api_key, payload)
