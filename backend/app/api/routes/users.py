from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    get_current_active_superuser,
)
from app.core.supabase import supabase_service
from app.api.schemas.common_schemas import Message
from app.api.schemas.user_schemas import (
    UserResponse,
    UserListResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user information from Supabase.
    """
    return {
        "id": current_user["id"],
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "full_name": current_user.get("user_metadata", {}).get("full_name"),
        "is_active": True,  # Supabase users are active by default
        "is_superuser": current_user.get("app_metadata", {}).get("is_superuser", False),
    }


@router.patch("/me", response_model=UserResponse)
def update_user_me(*, current_user: CurrentUser, user_in: UserUpdateRequest) -> Any:
    """
    Update own user information in Supabase.
    """
    try:
        # Prepare user metadata update
        user_metadata = current_user.get("user_metadata", {})
        
        if user_in.full_name is not None:
            user_metadata["full_name"] = user_in.full_name
        
        # Update user in Supabase
        updated_user = supabase_service.update_user_metadata(
            current_user["id"], 
            user_metadata
        )
        
        return {
            "id": updated_user["id"],
            "email": updated_user.get("email"),
            "phone": updated_user.get("phone"),
            "full_name": updated_user.get("user_metadata", {}).get("full_name"),
            "is_active": True,
            "is_superuser": updated_user.get("app_metadata", {}).get("is_superuser", False),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/me/password", response_model=Message)
def update_password_me(*, current_user: CurrentUser, body: ChangePasswordRequest) -> Any:
    """
    Update own password in Supabase.
    """
    # Note: Supabase handles password updates through their auth flow
    # This endpoint could redirect to Supabase password reset
    raise HTTPException(
        status_code=400, 
        detail="Password updates should be handled through Supabase Auth UI or password reset flow"
    )


@router.delete("/me", response_model=Message)
def delete_user_me(current_user: CurrentUser) -> Any:
    """
    Delete own user account from Supabase.
    """
    try:
        supabase_service.delete_user(current_user["id"])
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserListResponse)
def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users from Supabase (admin only).
    """
    try:
        # Calculate page number for Supabase pagination
        page = (skip // limit) + 1
        
        result = supabase_service.list_users(page=page, per_page=limit)
        
        users_data = []
        for user in result["users"]:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "full_name": user.user_metadata.get("full_name") if user.user_metadata else None,
                "is_active": True,
                "is_superuser": user.app_metadata.get("is_superuser", False) if user.app_metadata else False,
            })
        
        return UserListResponse(
            users=users_data,
            total_count=len(users_data),
            page=(skip // limit) + 1,
            page_size=limit,
            has_next=len(users_data) == limit,
            has_previous=skip > 0
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
