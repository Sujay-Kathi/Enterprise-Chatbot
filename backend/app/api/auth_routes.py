"""Authentication routes: Request OTP via email and verify to get JWT."""

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import EmailStr, BaseModel
from loguru import logger

from app.core import security
from app.services.email_service import send_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest):
    """Generate and send a 6-digit OTP to the user's email."""
    email = payload.email
    otp = security.generate_otp()
    security.store_otp(email, otp)
    
    try:
        await send_otp_email(email, otp)
        return {"message": f"OTP has been sent to {email}"}
    except Exception as e:
        logger.error(f"Failed to send OTP to {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please check server configuration."
        )

@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(payload: VerifyOTPRequest):
    """Verify OTP and return a JWT access token."""
    is_valid = security.verify_otp(payload.email, payload.otp)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP."
        )
    
    access_token = security.create_access_token(subject=payload.email)
    return {"access_token": access_token, "token_type": "bearer"}
