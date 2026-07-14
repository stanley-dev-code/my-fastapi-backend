import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Form, File, UploadFile
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user_model import User, UserRole
from app.schemas.user_schema import (
    UserResponse,
    UserUpdate,
    AdminCreateUser,
    UserRoleUpdate,
    ChangePassword,
)
from app.services import user_service
from app.utils.dependencies import (
    get_current_user,
    require_admin,
    require_super_admin,
    require_roles,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    full_name: str = Form(...),
    email: str = Form(...),
    bio: str | None = Form(None),
    date_of_birth: str | None = Form(None),
    gender: str | None = Form(None),
    nationality: str | None = Form(None),
    phone_number: str | None = Form(None),
    address: str | None = Form(None),
    profile_photo: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = UserUpdate(
        full_name=full_name,
        email=email,
        bio=bio,
        date_of_birth=date_of_birth,
        gender=gender,
        nationality=nationality,
        phone_number=phone_number,
        address=address,
    )

    user = user_service.update_user(
        db=db,
        user_id=current_user.id,
        data=data,
    )

    return user

@router.patch("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.change_password(
        db=db,
        user=current_user,
        old_password=data.old_password,
        new_password=data.new_password,
    )

    return {
        "message": "Password changed successfully"
    }


@router.delete("/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_service.delete_user(db, current_user.id)

    return {
        "message": "Account deleted successfully",
    }


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return user_service.get_users(db)


@router.post(
    "/admin/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def admin_create_user(
    data: AdminCreateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = user_service.admin_create_user(db, data)

    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    return user


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_super_admin),
):
    user = user_service.update_user_role(
        db=db,
        user_id=user_id,
        role=data.role,
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.delete("/{user_id}")
def admin_delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = user_service.delete_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "User deleted successfully",
    }


@router.get("/admin-only")
def admin_only_test(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Only admins can access this route",
        "user": current_user.email,
        "role": current_user.role,
    }              


@router.get("/super-admin-only")
def super_admin_only_test(
    current_user: User = Depends(require_super_admin),
):
    return {
        "message": "Only super admins can access this route",
        "user": current_user.email,
        "role": current_user.role,
    }


@router.get("/custom-role-access")
def custom_role_access(
    current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ),
):
    return {
        "message": "Custom role access granted",
        "user": current_user.email,
    }