from typing import AsyncGenerator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import TokenPayload
from app import crud

# OAuth2 scheme for JWT tokens
# This tells FastAPI to look for a Bearer token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    This is what you'll inject into every endpoint that needs database access.
    The session is automatically created, used, and cleaned up.
    
    Usage in endpoint:
        async def some_endpoint(db: AsyncSession = Depends(get_db)):
            # use db here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """
    Dependency that validates JWT token and returns the current user.
    
    This is how you protect endpoints - if the token is invalid or the user
    doesn't exist, this raises an HTTP 401 error automatically.
    
    Usage in endpoint:
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            # current_user is guaranteed to be valid here
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception
    
    # Get the user from database
    user = await crud.user.get(db, id=int(token_data.sub))
    if not user:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency that ensures the current user is active.
    
    This builds on get_current_user - it first validates the token,
    then also checks if the user account is active.
    
    This is dependency chaining - get_current_active_user depends on
    get_current_user, which depends on get_db and oauth2_scheme.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency for admin-only endpoints.
    
    Ensures the user is authenticated AND is a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user