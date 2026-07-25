from __future__ import annotations

from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class CustomerRecord(Base):
    """Placeholder ORM model for customer-related records."""

    __tablename__ = "customer_records"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    source = Column(String, nullable=True)
