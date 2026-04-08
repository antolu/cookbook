from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from cookbook.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    language = Column(String(20), default="en")

    # Basic recipe info
    description = Column(Text)
    servings = Column(String(100))  # renamed from 'makes'

    # Timing
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    total_time = Column(Integer)  # computed or manual override
    temperature = Column(Integer, default=0)

    # Content (will be stored as Markdown after migration)
    content = Column(Text)  # Full Markdown content
    ingredients_json = Column(JSON)  # Legacy JSON format during transition
    instructions_json = Column(JSON)  # Legacy JSON format during transition

    # Additional content
    changelog = Column(JSON)
    notes: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    tips: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    # Recipe metadata
    difficulty = Column(String(20))  # easy, medium, hard
    cuisine = Column(String(50))
    category = Column(String(50))  # appetizer, main, dessert, etc.
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50))
    )  # dietary restrictions, cooking methods, etc.

    # Media
    image_url = Column(String(500))

    # Visibility and features
    is_public = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Author (optional, only used in integrated mode)
    author_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(
        DateTime
    )  # renamed from pub_date, can be different from created_at

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, name='{self.name}')>"
