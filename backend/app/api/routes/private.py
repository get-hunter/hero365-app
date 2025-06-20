from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.deps import CurrentUser
from app.api.schemas.user_schemas import UserResponse

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserResponse)
def create_user(user_in: PrivateUserCreate) -> Any:
    """
    Create a new user.
    
    NOTE: This endpoint is temporarily disabled during clean architecture migration.
    Will be properly implemented in Phase 4 using clean architecture patterns.
    """
    # TODO: Implement using CreateUserUseCase in Phase 4
    from fastapi import HTTPException
    
    raise HTTPException(
        status_code=501, 
        detail="Create user endpoint temporarily disabled during architecture migration"
    )
