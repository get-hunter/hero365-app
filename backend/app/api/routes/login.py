from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, get_current_active_superuser
from app.core.config import settings
from app.api.schemas.common_schemas import Message
from app.api.schemas.auth_schemas import NewPassword, Token
from app.api.schemas.user_schemas import UserResponse

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    
    NOTE: This endpoint is temporarily disabled during clean architecture migration.
    Will be properly implemented in Phase 4 using clean architecture patterns.
    """
    # TODO: Implement using AuthenticateUserUseCase in Phase 4
    raise HTTPException(
        status_code=501, 
        detail="Login endpoint temporarily disabled during architecture migration"
    )


@router.post("/login/test-token", response_model=UserResponse)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str) -> Message:
    """
    Password Recovery
    
    NOTE: This endpoint is temporarily disabled during clean architecture migration.
    Will be properly implemented in Phase 4 using clean architecture patterns.
    """
    # TODO: Implement using ResetPasswordUseCase in Phase 4
    raise HTTPException(
        status_code=501, 
        detail="Password recovery endpoint temporarily disabled during architecture migration"
    )


@router.post("/reset-password/")
def reset_password(body: NewPassword) -> Message:
    """
    Reset password
    
    NOTE: This endpoint is temporarily disabled during clean architecture migration.
    Will be properly implemented in Phase 4 using clean architecture patterns.
    """
    # TODO: Implement using ResetPasswordUseCase in Phase 4
    raise HTTPException(
        status_code=501, 
        detail="Reset password endpoint temporarily disabled during architecture migration"
    )


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str) -> Any:
    """
    HTML Content for Password Recovery
    
    NOTE: This endpoint is temporarily disabled during clean architecture migration.
    Will be properly implemented in Phase 4 using clean architecture patterns.
    """
    # TODO: Implement using ResetPasswordUseCase in Phase 4
    raise HTTPException(
        status_code=501, 
        detail="Password recovery HTML endpoint temporarily disabled during architecture migration"
    )
