from typing import Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.supabase import supabase_service
from app.models import Message, UserPublic

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
def sign_up(signup_data: SignUpRequest) -> Message:
    """
    Sign up with email and password using Supabase Auth
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured. Please use the legacy signup endpoint."
        )
    
    try:
        user_metadata = {}
        if signup_data.full_name:
            user_metadata["full_name"] = signup_data.full_name
        
        response = supabase_service.create_user(
            email=signup_data.email,
            password=signup_data.password,
            user_metadata=user_metadata
        )
        
        return Message(message="User created successfully. Please check your email for verification.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/auth/signup/phone", response_model=Message)
def sign_up_with_phone(signup_data: PhoneSignUpRequest) -> Message:
    """
    Sign up with phone number using Supabase Auth
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    try:
        user_metadata = {}
        if signup_data.full_name:
            user_metadata["full_name"] = signup_data.full_name
        
        response = supabase_service.create_user_with_phone(
            phone=signup_data.phone,
            password=signup_data.password,
            user_metadata=user_metadata
        )
        
        return Message(message="User created successfully. Please verify your phone number.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/auth/signin")
def sign_in(signin_data: SignInRequest) -> dict:
    """
    Sign in with email and password using Supabase Auth
    Note: This endpoint is mainly for documentation. 
    Frontend should use Supabase client directly for sign in.
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured. Please use the legacy login endpoint."
        )
    
    try:
        response = supabase_service.client.auth.sign_in_with_password({
            "email": signin_data.email,
            "password": signin_data.password
        })
        
        if response.user and response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata,
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
def sign_in_with_phone(signin_data: PhoneSignInRequest) -> dict:
    """
    Sign in with phone number and password using Supabase Auth
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    try:
        response = supabase_service.client.auth.sign_in_with_password({
            "phone": signin_data.phone,
            "password": signin_data.password
        })
        
        if response.user and response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "phone": response.user.phone,
                    "user_metadata": response.user.user_metadata,
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
def send_otp(otp_data: SendOTPRequest) -> Message:
    """
    Send OTP to phone number for passwordless authentication
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    try:
        response = supabase_service.client.auth.sign_in_with_otp({
            "phone": otp_data.phone
        })
        
        return Message(message="OTP sent successfully to your phone number.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send OTP: {str(e)}"
        )


@router.post("/auth/otp/verify")
def verify_otp(verification_data: OTPVerificationRequest) -> dict:
    """
    Verify OTP for phone number authentication
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    try:
        response = supabase_service.client.auth.verify_otp({
            "phone": verification_data.phone,
            "token": verification_data.token,
            "type": "sms"
        })
        
        if response.user and response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "phone": response.user.phone,
                    "user_metadata": response.user.user_metadata,
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP"
        )


@router.get("/auth/oauth/{provider}")
def oauth_login(provider: str) -> dict:
    """
    Get OAuth login URL for Google, Apple, etc.
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    if provider not in ["google", "apple", "github", "facebook"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )
    
    try:
        # Return OAuth URL - frontend will handle the redirect
        oauth_url = f"{supabase_service.client.supabase_url}/auth/v1/authorize?provider={provider}"
        return {
            "url": oauth_url,
            "provider": provider
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )


@router.post("/auth/signout", response_model=Message)
def sign_out() -> Message:
    """
    Sign out - handled by Supabase client on frontend
    """
    return Message(message="Sign out should be handled by the frontend Supabase client")


@router.post("/auth/refresh")
def refresh_token(refresh_token: str) -> dict:
    """
    Refresh access token
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured."
        )
    
    try:
        response = supabase_service.client.auth.refresh_session(refresh_token)
        
        if response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/auth/password-recovery", response_model=Message)
def password_recovery(email: EmailStr) -> Message:
    """
    Send password recovery email via Supabase Auth
    """
    if not supabase_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured. Please use the legacy password recovery endpoint."
        )
    
    try:
        supabase_service.client.auth.reset_password_email(email)
        return Message(message="Password recovery email sent")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send password recovery email: {str(e)}"
        ) 