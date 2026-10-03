"""
Centralized AI Provider Manager with Transparent Failover.

Architecture & Provider Priority:
1. PRIMARY: Google Gemini (gemini-3.6-flash via google-genai SDK).
2. BACKUP / FALLBACK: OpenAI (via official openai SDK or direct REST API via requests/httpx if SDK is not installed).

Failover Policy:
- Gemini is always tried first.
- If Gemini succeeds, its text response is returned immediately.
- If Gemini encounters a TRANSIENT / AVAILABILITY error:
    * HTTP 429 (Rate limit / quota exhaustion)
    * HTTP 500, 502, 503, 504 (Server errors / overload)
    * Timeout / Network connection failures
    * ServiceUnavailable / ResourceExhausted exceptions
  AND an OPENAI_API_KEY is configured:
    -> Failover to OpenAI is initiated automatically.
- If Gemini encounters NON-TRANSIENT errors (e.g. ValueError, invalid parameters, authentication / key format errors):
    -> No fallback is attempted; the error is raised/handled directly.
- If OpenAI is NOT configured (no OPENAI_API_KEY) and Gemini encounters a transient error:
    -> A clear Gemini error is raised without failing the application or breaking startup.
- Security & Privacy:
    * API keys are NEVER logged or printed.
    * Full prompt content is NEVER logged (only character length or generic status).
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ai_provider_manager")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# Configured Models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Transient HTTP Status Codes that justify failover
TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504, 520, 521, 522, 524}


def is_transient_error(exception: Exception) -> bool:
    """
    Determine if an exception represents a transient/availability failure
    (e.g., rate limit, timeout, server overload, connection drop).
    Returns False for standard coding/validation/non-transient errors.
    """
    if exception is None:
        return False

    error_str = str(exception).lower()

    # Check status code attributes if present on API errors
    status_code = getattr(exception, "status_code", None) or getattr(exception, "code", None)
    if status_code and isinstance(status_code, int) and status_code in TRANSIENT_STATUS_CODES:
        return True

    # Common transient error keywords in message strings across SDKs
    transient_indicators = [
        "429", "rate limit", "quota", "resourceexhausted", "resource_exhausted",
        "500", "502", "503", "504", "service unavailable", "serviceunavailable",
        "server error", "overloaded", "deadline exceeded", "timeout", "timed out",
        "connection error", "connection refused", "connection reset", "network error",
        "remoteprotocolerror", "connecttimeout", "readtimeout"
    ]

    for indicator in transient_indicators:
        if indicator in error_str:
            return True

    # Check class name for known transient types
    exc_class_name = exception.__class__.__name__.lower()
    transient_classes = [
        "timeout", "timeouterror", "serviceunavailable", "resourceexhausted",
        "connectionerror", "connecterror", "ratelimiterror", "internalservererror"
    ]
    for cls in transient_classes:
        if cls in exc_class_name:
            return True

    return False


def _call_gemini(prompt: str) -> str:
    """
    Invoke Gemini using the official google-genai Client.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY is not configured in environment.")

    # Local import ensures graceful loading
    from google import genai

    client = genai.Client(api_key=gemini_key)
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    if not response or not hasattr(response, "text"):
        raise ValueError("Gemini returned an empty or invalid response object.")

    return response.text


def _call_openai(prompt: str) -> str:
    """
    Invoke OpenAI backup.
    Supports official `openai` SDK if installed, or falls back to direct
    REST API call via requests/httpx if the openai package is not yet installed.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    # 1. Try official openai SDK if available in environment
    try:
        import openai
        client = openai.OpenAI(api_key=openai_key)
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content or ""
        raise ValueError("OpenAI SDK returned empty response choices.")
    except ImportError:
        pass  # SDK not installed, fallback to direct REST call below

    # 2. Direct REST API via requests (installed in environment)
    import requests
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=45
    )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI REST API returned status {resp.status_code}")

    data = resp.json()
    choices = data.get("choices", [])
    if choices and "message" in choices[0]:
        return choices[0]["message"].get("content", "")
    raise ValueError("OpenAI REST response did not contain expected message format.")


def ask_ai(prompt: str) -> str:
    """
    Central AI entrypoint with transparent failover.

    1. Attempts Gemini first.
    2. If Gemini succeeds, returns its response directly.
    3. If Gemini encounters a transient error (429, 5xx, timeout) AND OPENAI_API_KEY is present:
       Logs the switch and routes to OpenAI.
    4. If Gemini fails with non-transient error, re-raises the original Gemini error.
    5. If Gemini fails and OpenAI is not configured, re-raises the clean Gemini error.
    """
    gemini_error: Optional[Exception] = None

    try:
        return _call_gemini(prompt)
    except Exception as e:
        gemini_error = e

    # Determine if fallback should be triggered
    openai_key = os.getenv("OPENAI_API_KEY")
    transient = is_transient_error(gemini_error)

    if transient and openai_key:
        logger.warning(
            "Primary AI provider (Gemini) encountered a transient availability issue (%s). "
            "Initiating failover to backup provider (OpenAI)...",
            gemini_error.__class__.__name__
        )
        try:
            openai_response = _call_openai(prompt)
            logger.info("Failover to backup AI provider (OpenAI) succeeded.")
            return openai_response
        except Exception as backup_error:
            logger.error(
                "Backup AI provider (OpenAI) also encountered an error (%s).",
                backup_error.__class__.__name__
            )
            # Re-raise the primary Gemini error to maintain compatibility with existing handlers
            raise gemini_error from backup_error

    if not transient:
        logger.debug("Non-transient error from primary provider; skipping backup failover.")

    # Re-raise the original Gemini exception
    raise gemini_error


# Backwards compatibility alias
def ask_gemini(prompt: str) -> str:
    """
    Drop-in replacement for legacy ask_gemini calls across main.py and other services.
    Routes through the centralized provider manager with failover.
    """
    return ask_ai(prompt)
