from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Customer(Base):

    __tablename__ = "customers" 

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_name_normalized: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    business_type_normalized: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[str] = mapped_column(String(60), nullable=False, default="registry-api")


# idempotency_key: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    #request_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    #response_cache: Mapped[Optional[str]] = mapped_column(Text, nullable=True)