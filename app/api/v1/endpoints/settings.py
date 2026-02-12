"""
User settings endpoints: account, email, password, 2FA, delete account.
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.settings import (
    SettingsDataOut,
    UpdateAccountRequest,
    UpdateEmailRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
)
from app.services.settings_service import SettingsService
from app.services.auth_service import AuthService
from app.utils.email import send_email

router = APIRouter()


@router.get("", response_model=SettingsDataOut)
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's settings (account, email, security flags)."""
    service = SettingsService(db)
    return service.get_settings(current_user)


@router.patch("/account", response_model=SettingsDataOut)
async def update_account(
    payload: UpdateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update display name and/or username."""
    service = SettingsService(db)
    try:
        service.update_account(current_user, payload)
        return service.get_settings(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/email", response_model=SettingsDataOut)
async def update_email(
    payload: UpdateEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update email address. User may need to sign in again with the new email."""
    service = SettingsService(db)
    try:
        service.update_email(current_user, payload.email)
        return service.get_settings(current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/email/verify")
async def verify_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Request email verification.

    Sends an email with a one-time verification link. When the user clicks
    the link, their email will be marked as verified.
    """
    auth_service = AuthService(db)
    token = auth_service.create_access_token(
        data={"sub": str(current_user.id), "scope": "email_verify"},
        expires_delta=timedelta(hours=24),
    )

    # Frontend page that will call the confirm API and show a nice UI
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify your email address"
    text_body = (
        f"Hi,\n\n"
        f"Please verify your email address for {settings.PROJECT_NAME} by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"If you did not request this, you can safely ignore this email."
    )
    html_body = f"""
    <html>
      <body>
        <p>Hi,</p>
        <p>Please verify your email address for <strong>{settings.PROJECT_NAME}</strong> by clicking the button below:</p>
        <p style="margin:24px 0;">
          <a href="{verify_url}"
             style="background-color:#2563EB;color:#ffffff;padding:10px 18px;border-radius:6px;
                    text-decoration:none;font-weight:600;display:inline-block;">
            Verify email
          </a>
        </p>
        <p>If the button does not work, copy and paste this URL into your browser:</p>
        <p><a href="{verify_url}">{verify_url}</a></p>
        <p>If you did not request this, you can safely ignore this email.</p>
      </body>
    </html>
    """

    try:
        send_email(current_user.email, subject, text_body, html_body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email.",
        )

    return {"message": "Verification email sent. Check your inbox."}


@router.get("/email/verify/confirm")
async def confirm_email(
    token: str,
    db: Session = Depends(get_db),
):
    """
    Verify email address from the token in the email link.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        scope = payload.get("scope")
        sub = payload.get("sub")
        if scope != "email_verify" or sub is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")
        try:
            user_id = int(sub)
        except (TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")

    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.email_verified = True
    db.commit()

    # JSON response so the frontend page can show a rich UI.
    return {"message": "Email verified."}


@router.post("/password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password. Requires current password."""
    service = SettingsService(db)
    try:
        service.change_password(current_user, payload.current_password, payload.new_password)
        return {"message": "Password updated."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/2fa")
async def enable_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enable two-factor authentication. (Stub: full flow would set up TOTP.)"""
    service = SettingsService(db)
    service.enable_2fa(current_user)
    return {"message": "2FA enabled.", "twoFactorEnabled": True}


@router.delete("/account/delete")
async def delete_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete account (deactivate). Requires confirmation body: { \"confirmation\": \"DELETE\" }."""
    service = SettingsService(db)
    try:
        service.delete_account(current_user, payload.confirmation)
        return {"message": "Account deactivated."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
