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


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: dict


@router.post("/auth/signup", response_model=Message)
def sign_up(signup_data: SignUpRequest) -> Message:
    """
    Sign up with Supabase Auth
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


@router.post("/auth/signin")
def sign_in(signin_data: SignInRequest) -> dict:
    """
    Sign in with Supabase Auth
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