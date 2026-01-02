from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()

# Include all endpoint routers with their prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# As you add more endpoints, include them here:
# api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
# api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
