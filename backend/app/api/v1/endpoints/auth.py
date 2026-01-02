import logging
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.schemas.user import User, Token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    db: Annotated[AsyncSession, Depends(deps.get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
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
    logger.info(f"Login attempt for user: {form_data.username}")
    user = await crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        logger.warning(
            f"Failed login attempt for: {form_data.username} - Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        logger.warning(f"Failed login attempt for user ID {user.id} - Account inactive")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Create access token with user ID as subject
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    logger.info(f"Successful login for user ID: {user.id} ({user.email})")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/test-token", response_model=User)
async def test_token(
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Any:
    """
    Test endpoint to verify JWT token works.

    This is useful during development to verify your token is valid.
    Just hit this endpoint with a token and if you get your user data back,
    the token is working correctly.
    """
    return current_user
