from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    get_current_active_superuser,
)
from app.core.auth_facade import auth_facade
from app.api.schemas.common_schemas import Message
from app.api.schemas.user_schemas import (
    UserResponse,
    UserListResponse,
    UserUpdateRequest,
    ChangePasswordRequest,
    OnboardingCompletedRequest,
    OnboardingCompletedResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user information from Supabase.
    """
    user_metadata = current_user.get("user_metadata", {})
    onboarding_data = auth_facade.get_onboarding_data(user_metadata)
    
    return {
        "id": current_user["id"],
        "email": current_user.get("email"),
        "phone": current_user.get("phone"),
        "full_name": user_metadata.get("full_name"),
        "is_active": True,  # Supabase users are active by default
        "is_superuser": current_user.get("app_metadata", {}).get("is_superuser", False),
        "onboarding_completed": onboarding_data["onboarding_completed"],
        "onboarding_completed_at": onboarding_data["onboarding_completed_at"],
        "completed_steps": onboarding_data["completed_steps"],
    }


@router.patch("/me", response_model=UserResponse)
async def update_user_me(*, current_user: CurrentUser, user_in: UserUpdateRequest) -> Any:
    """
    Update own user information in Supabase.
    """
    try:
        # Prepare user metadata update
        user_metadata = current_user.get("user_metadata", {})
        
        if user_in.full_name is not None:
            user_metadata["full_name"] = user_in.full_name
        
        # Update user in Supabase
        updated_user = await auth_facade.update_user_metadata(
            current_user["id"], 
            user_metadata
        )
        
        return {
            "id": updated_user.id if hasattr(updated_user, 'id') else updated_user["id"],
            "email": updated_user.email if hasattr(updated_user, 'email') else updated_user.get("email"),
            "phone": updated_user.phone if hasattr(updated_user, 'phone') else updated_user.get("phone"),
            "full_name": user_metadata.get("full_name"),
            "is_active": True,
            "is_superuser": user_metadata.get("is_superuser", False),
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
async def delete_user_me(current_user: CurrentUser) -> Any:
    """
    Delete own user account from Supabase.
    """
    try:
        success = await auth_facade.delete_user(current_user["id"])
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete user")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/onboarding-completed", response_model=OnboardingCompletedResponse)
async def mark_onboarding_completed(
    *, 
    current_user: CurrentUser, 
    request: OnboardingCompletedRequest
) -> Any:
    """
    Mark user onboarding as completed.
    """
    try:
        from datetime import datetime
        
        # Use current timestamp if not provided
        completion_date = request.completion_date or datetime.utcnow()
        
        # Update user metadata with onboarding completion
        result = await auth_facade.mark_onboarding_completed(
            current_user["id"],
            completed_steps=request.completed_steps,
            completion_date=completion_date.isoformat()
        )
        
        return OnboardingCompletedResponse(
            success=True,
            message="Onboarding marked as completed successfully",
            onboarding_completed=True,
            completed_at=completion_date
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserListResponse)
async def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users from Supabase (admin only).
    """
    try:
        # Calculate page number for Supabase pagination
        page = (skip // limit) + 1
        
        result = await auth_facade.list_users(page=page, per_page=limit)
        
        users_data = []
        for user in result["users"]:
            # Handle both old and new user data structure
            if hasattr(user, 'metadata'):
                user_metadata = user.metadata or {}
            else:
                user_metadata = getattr(user, 'user_metadata', {}) or {}
                
            users_data.append({
                "id": user.id,
                "email": user.email,
                "phone": getattr(user, 'phone', None),
                "full_name": user_metadata.get("full_name"),
                "is_active": True,
                "is_superuser": user_metadata.get("is_superuser", False),
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
