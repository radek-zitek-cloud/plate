from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# Type variables for generic class
ModelType = TypeVar("ModelType", bound=Base)  # Any SQLAlchemy model
CreateSchemaType = TypeVar(
    "CreateSchemaType", bound=BaseModel
)  # Pydantic create schema
UpdateSchemaType = TypeVar(
    "UpdateSchemaType", bound=BaseModel
)  # Pydantic update schema


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD operations.

    This class is generic over three types:
    - ModelType: The SQLAlchemy model (e.g., User)
    - CreateSchemaType: The Pydantic schema for creation (e.g., UserCreate)
    - UpdateSchemaType: The Pydantic schema for updates (e.g., UserUpdate)
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize with the SQLAlchemy model.

        Args:
            model: The SQLAlchemy model class (e.g., User)
        """
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Retrieve a single record by ID.

        This is the generic "retrieve" operation. It works for any model
        because we're using self.model which was passed during initialization.
        """
        result = await db.execute(select(self.model).where(self.model.id == id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Retrieve multiple records with pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        This converts the Pydantic schema to a dict, then creates the SQLAlchemy
        model instance. The model type comes from self.model.

        Args:
            obj_in: Pydantic schema with creation data (e.g., UserCreate)

        Returns:
            The created SQLAlchemy model instance
        """
        obj_in_data = jsonable_encoder(obj_in)  # Convert Pydantic to dict
        db_obj = self.model(**obj_in_data)  # Create model instance
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update an existing record.

        This handles partial updates - only the fields provided in obj_in
        get updated. Fields not included remain unchanged.

        Args:
            db_obj: The existing SQLAlchemy model instance to update
            obj_in: Either a Pydantic schema or dict with update data

        Returns:
            The updated SQLAlchemy model instance
        """
        obj_data = jsonable_encoder(db_obj)  # Convert current state to dict

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(
                exclude_unset=True
            )  # Only fields that were set

        # Update only the fields that were provided
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Delete a record by ID.

        Returns the deleted object if it existed, None otherwise.
        """
        obj = await self.get(db, id=id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
