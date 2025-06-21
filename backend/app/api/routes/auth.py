from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.auth_facade import auth_facade
from app.infrastructure.config.dependency_injection import get_container
from app.api.schemas.common_schemas import Message

from app.api.schemas.auth_schemas import (
    AppleSignInRequest,
    GoogleSignInRequest, 
    OAuthSignInResponse,
)
from app.api.controllers.oauth_controller import OAuthController

router = APIRouter(tags=["auth"])


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class PhoneSignUpRequest(BaseModel):
    phone: str
    password: str
    full_name: str | None = None


class PhoneSignInRequest(BaseModel):
    phone: str
    password: str


class OTPVerificationRequest(BaseModel):
    phone: str
    token: str


class SendOTPRequest(BaseModel):
    phone: str


class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


@router.post("/auth/signup", response_model=Message)
async def sign_up(signup_data: SignUpRequest) -> Message:
    """
    Sign up with email and password using Supabase Auth
    """
    try:
        user_metadata = {}
        if signup_data.full_name:
            user_metadata["full_name"] = signup_data.full_name
        
        response = await auth_facade.create_user(
            email=signup_data.email,
            password=signup_data.password,
            user_metadata=user_metadata
        )
        
        return Message(message="User created successfully. Please check your email for verification.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/auth/signup/phone", response_model=Message)
async def sign_up_with_phone(signup_data: PhoneSignUpRequest) -> Message:
    """
    Sign up with phone number using Supabase Auth
    """
    try:
        user_metadata = {}
        if signup_data.full_name:
            user_metadata["full_name"] = signup_data.full_name
        
        response = await auth_facade.create_user_with_phone(
            phone=signup_data.phone,
            password=signup_data.password,
            user_metadata=user_metadata
        )
        
        return Message(message="User created successfully. Please verify your phone number.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/auth/signin")
async def sign_in(signin_data: SignInRequest) -> dict:
    """
    Sign in with email and password using Supabase Auth
    Note: This endpoint is mainly for documentation. 
    Frontend should use Supabase client directly for sign in.
    """
    try:
        # Use auth service from container for direct authentication
        auth_service = get_container().get_auth_service()
        auth_result = await auth_service.authenticate_with_email(
            signin_data.email, 
            signin_data.password
        )
        
        if auth_result.success and auth_result.user and auth_result.token:
            user_metadata = auth_result.user.metadata or {}
            onboarding_data = auth_facade.get_onboarding_data(user_metadata)
            
            return {
                "access_token": auth_result.token.access_token,
                "refresh_token": auth_result.token.refresh_token,
                "user": {
                    "id": auth_result.user.id,
                    "email": auth_result.user.email,
                    "user_metadata": user_metadata,
                    "onboarding_completed": onboarding_data["onboarding_completed"],
                    "onboarding_completed_at": onboarding_data["onboarding_completed_at"],
                    "completed_steps": onboarding_data["completed_steps"]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/auth/signin/phone")
async def sign_in_with_phone(signin_data: PhoneSignInRequest) -> dict:
    """
    Sign in with phone number and password using Supabase Auth
    """
    try:
        # Use auth service from container for direct authentication
        auth_service = get_container().get_auth_service()
        auth_result = await auth_service.authenticate_with_phone(
            signin_data.phone, 
            signin_data.password
        )
        
        if auth_result.success and auth_result.user and auth_result.token:
            user_metadata = auth_result.user.metadata or {}
            onboarding_data = auth_facade.get_onboarding_data(user_metadata)
            
            return {
                "access_token": auth_result.token.access_token,
                "refresh_token": auth_result.token.refresh_token,
                "user": {
                    "id": auth_result.user.id,
                    "phone": auth_result.user.phone,
                    "user_metadata": user_metadata,
                    "onboarding_completed": onboarding_data["onboarding_completed"],
                    "onboarding_completed_at": onboarding_data["onboarding_completed_at"],
                    "completed_steps": onboarding_data["completed_steps"]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/auth/otp/send", response_model=Message)
async def send_otp(otp_data: SendOTPRequest) -> Message:
    """
    Send OTP to phone number for passwordless authentication
    """
    try:
        success = await auth_facade.send_otp(otp_data.phone)
        if success:
            return Message(message="OTP sent successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send OTP"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/auth/otp/verify")
async def verify_otp(verification_data: OTPVerificationRequest) -> dict:
    """
    Verify OTP for phone number authentication
    """
    try:
        response = await auth_facade.verify_otp(
            verification_data.phone,
            verification_data.token
        )
        
        user_data = response.get("user")
        session_data = response.get("session")
        
        if user_data and session_data:
            user_metadata = getattr(user_data, 'metadata', {}) or {}
            onboarding_data = auth_facade.get_onboarding_data(user_metadata)
            
            return {
                "access_token": session_data.access_token,
                "refresh_token": session_data.refresh_token,
                "user": {
                    "id": user_data.id,
                    "phone": user_data.phone,
                    "user_metadata": user_metadata,
                    "onboarding_completed": onboarding_data["onboarding_completed"],
                    "onboarding_completed_at": onboarding_data["onboarding_completed_at"],
                    "completed_steps": onboarding_data["completed_steps"]
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP verification failed"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP verification failed"
        )


@router.get("/auth/oauth/{provider}")
def oauth_login(provider: str) -> dict:
    """
    OAuth login endpoint - returns redirect URL for OAuth flow
    """
    if provider not in ["google", "apple"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    # For mobile apps, this would typically return the OAuth provider's authorization URL
    # Since we're using server-side token validation, this is mainly for documentation
    return {
        "message": f"Use {provider} SDK in your mobile app to get ID token, then call the appropriate sign-in endpoint",
        "endpoints": {
            "apple": "/auth/apple/signin",
            "google": "/auth/google/signin"
        }
    }


@router.post("/auth/signout", response_model=Message)
def sign_out() -> Message:
    """
    Sign out endpoint - client should handle token cleanup
    """
    return Message(message="Signed out successfully. Please clear tokens on client side.")


@router.post("/auth/refresh")
async def refresh_token(refresh_token: str) -> dict:
    """
    Refresh access token using refresh token
    """
    try:
        auth_service = get_container().get_auth_service()
        auth_result = await auth_service.refresh_token(refresh_token)
        
        if auth_result.success and auth_result.token:
            return {
                "access_token": auth_result.token.access_token,
                "refresh_token": auth_result.token.refresh_token,
                "expires_in": getattr(auth_result.token, 'expires_in', 3600),
                "token_type": "bearer"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to refresh token"
        )


@router.post("/auth/password-recovery", response_model=Message)
async def password_recovery(email: EmailStr) -> Message:
    """
    Request password recovery email
    """
    try:
        auth_service = get_container().get_auth_service()
        success = await auth_service.reset_password(email)
        
        if success:
            return Message(message="Password recovery email sent")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to send password recovery email"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send password recovery email: {str(e)}"
        )


@router.post("/auth/apple/signin", response_model=OAuthSignInResponse)
async def apple_sign_in(request: AppleSignInRequest) -> OAuthSignInResponse:
    """
    Handle Apple Sign-In using ID token from iOS app
    """
    controller = OAuthController()
    return await controller.apple_sign_in(request)


@router.post("/auth/google/signin", response_model=OAuthSignInResponse)
async def google_sign_in(request: GoogleSignInRequest) -> OAuthSignInResponse:
    """
    Handle Google Sign-In using ID token from iOS app
    """
    controller = OAuthController()
    return await controller.google_sign_in(request) 