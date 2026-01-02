from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.core.password_validator import validate_password_or_raise


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD operations for User model.

    Inherits all the basic CRUD operations from CRUDBase.
    We only need to add user-specific operations here.
    """

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """
        User-specific operation: find user by email.

        This is unique to User - not every model needs email lookup.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """
        User-specific operation: find user by username.
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """
        Override the base create method to handle password hashing.

        This is why we have user-specific CRUD - User creation needs
        special handling that other models don't need.
        """
        # Validate password strength before creating user
        validate_password_or_raise(obj_in.password)

        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),  # Hash the password
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        """
        Override update to handle password hashing if password is being updated.
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        # If password is being updated, validate and hash it
        if "password" in update_data:
            validate_password_or_raise(update_data["password"])
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        # Use parent class's update logic for the rest
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
        self, db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        User-specific operation: authenticate with email and password.

        This combines get_by_email with password verification.
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def is_active(self, user: User) -> bool:
        """Helper to check if user is active."""
        return user.is_active

    async def is_superuser(self, user: User) -> bool:
        """Helper to check if user is superuser."""
        return user.is_superuser


# Create an instance to use throughout the app
user = CRUDUser(User)
