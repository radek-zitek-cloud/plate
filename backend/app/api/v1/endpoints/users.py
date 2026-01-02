import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.api import deps
from app.models.user import User
from app.core.password_validator import PasswordValidationError
from app.core.rate_limit import limiter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
) -> Any:
    """
    Get current user.

    This endpoint returns the authenticated user's own data.
    Notice how we use Depends(deps.get_current_active_user) to:
    1. Validate the JWT token
    2. Load the user from database
    3. Check user is active

    All of that happens automatically before this function runs.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_in: schemas.UserUpdate,
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
) -> Any:
    """
    Update current user.

    Users can update their own information. The user_in schema defines
    what fields can be updated (email, username, full_name, etc.).
    Note: For password changes, use the dedicated /me/password endpoint.
    """
    # Check if email is being changed and already exists
    if user_in.email and user_in.email != current_user.email:
        existing_user = await crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="A user with this email already exists"
            )

    # Check if username is being changed and already exists
    if user_in.username and user_in.username != current_user.username:
        existing_user = await crud.user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="A user with this username already exists"
            )

    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    logger.info(f"User profile updated for user ID: {current_user.id}")
    return user


@router.post("/me/password")
async def change_password(
    password_change: schemas.PasswordChange,
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
) -> Any:
    """
    Change current user's password.

    Requires the current password for verification before setting new password.
    This provides an extra layer of security.
    """
    from app.core.security import verify_password

    # Verify current password
    if not verify_password(
        password_change.current_password, current_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Update password
    try:
        user_update = schemas.UserUpdate(password=password_change.new_password)
        await crud.user.update(db, db_obj=current_user, obj_in=user_update)
        logger.info(f"Password changed for user ID: {current_user.id}")
        return {"message": "Password updated successfully"}
    except PasswordValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/signup", response_model=schemas.User)
@limiter.limit("3/hour")
async def create_user_signup(
    request: Request,
    user_in: schemas.UserCreate,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
) -> Any:
    """
    Create new user without requiring authentication.

    This is your public signup endpoint. Notice it doesn't require
    any authentication dependencies - anyone can hit this.

    Flow:
    1. Client sends user data (email, username, password)
    2. We check if email/username already exists
    3. If not, create the user (password gets hashed in crud.user.create)
    4. Return the new user data (without password)
    """
    # Check if email already registered
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400, detail="A user with this email already exists"
        )

    # Check if username already taken
    user = await crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400, detail="A user with this username already exists"
        )

    # Create new user
    try:
        user = await crud.user.create(db, obj_in=user_in)
        logger.info(f"New user created: {user.email} (ID: {user.id})")
        return user
    except PasswordValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: int,
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
) -> Any:
    """
    Get a specific user by ID.

    This is a protected endpoint - requires authentication.
    Any authenticated user can view other users' public information.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional: Add permission check
    # if user == current_user:
    #     return user
    # if not current_user.is_superuser:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    return user


@router.get("/", response_model=list[schemas.User])
async def read_users(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    current_user: Annotated[User, Depends(deps.get_current_superuser)],
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users (admin only).

    Notice this uses get_current_superuser - only superusers can list all users.
    The skip and limit parameters provide pagination.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    user_id: int,
    current_user: Annotated[User, Depends(deps.get_current_superuser)],
    db: Annotated[AsyncSession, Depends(deps.get_db)],
) -> Any:
    """
    Delete a user (admin only).

    Only superusers can delete users. This is a hard delete - the user
    is removed from the database entirely.

    Consider using a soft delete (setting is_active=False) instead for
    production systems.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = await crud.user.delete(db, id=user_id)
    return user
