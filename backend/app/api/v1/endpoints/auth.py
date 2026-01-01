from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import User, Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 compatible token login.
    
    This endpoint receives username and password in form data format
    (required by OAuth2 spec) and returns a JWT access token.
    
    Flow:
    1. Receive credentials from client
    2. Authenticate user (check password)
    3. Generate JWT token
    4. Return token to client
    
    The client then includes this token in subsequent requests:
    Authorization: Bearer <token>
    """
    # Authenticate user with email and password
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access token with user ID as subject
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/test-token", response_model=User)
async def test_token(
    current_user: Annotated[User, Depends(deps.get_current_user)]
) -> Any:
    """
    Test endpoint to verify JWT token works.
    
    This is useful during development to verify your token is valid.
    Just hit this endpoint with a token and if you get your user data back,
    the token is working correctly.
    """
    return current_user