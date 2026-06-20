from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.config import settings
from api.routes.auth import get_current_user
from models.user import User
from datetime import datetime, timedelta, timezone
from loguru import logger
import uuid
import httpx

router = APIRouter(prefix="/auth/gmail", tags=["gmail"])

SCOPES = "https://www.googleapis.com/auth/gmail.send"
REDIRECT_URI = f"{settings.backend_url}/api/auth/gmail/callback"


@router.get("/connect")
async def gmail_connect(current_user: User = Depends(get_current_user)):
    """Initiate Gmail OAuth flow — build the URL manually, no PKCE."""
    from urllib.parse import urlencode

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": str(current_user.id),
        "include_granted_scopes": "true",
    }
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"auth_url": auth_url}


@router.get("/callback")
async def gmail_callback(
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
):
    """Handle Gmail OAuth callback — manual token exchange, no PKCE."""
    async with httpx.AsyncClient() as http_client:
        res = await http_client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )

    if res.status_code != 200:
        logger.error(f"Gmail token exchange failed: {res.status_code} - {res.text}")
        raise HTTPException(status_code=400, detail=f"Gmail auth failed: {res.text}")

    token_data = res.json()

    user = await db.get(User, uuid.UUID(state))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.gmail_access_token = token_data["access_token"]
    if "refresh_token" in token_data:
        user.gmail_refresh_token = token_data["refresh_token"]
    if "expires_in" in token_data:
        user.gmail_token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_data["expires_in"])

    await db.commit()
    logger.info(f"DEBUG expiry={user.gmail_token_expiry} access_token_set={bool(user.gmail_access_token)}")
    logger.info(f"Gmail connected for user {state}")
    return RedirectResponse(url=f"{settings.frontend_url}/profile?gmail=connected")


@router.get("/status")
async def gmail_status(current_user: User = Depends(get_current_user)):
    """Check if Gmail is connected."""
    connected = bool(current_user.gmail_access_token)
    expired = False
    if current_user.gmail_token_expiry:
        expiry = current_user.gmail_token_expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        expired = expiry < datetime.now(timezone.utc)

    return {
        "connected": connected and not expired,
        "needs_reconnect": connected and expired,
    }