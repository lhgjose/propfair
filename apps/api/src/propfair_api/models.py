from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Boolean, ARRAY, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Listing(Base):
    """Listing model representing rental properties."""
    __tablename__ = "listings"

    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True)

    # External reference
    external_id: Mapped[str] = mapped_column("external_id", String)
    source: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

    # Basic info
    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Pricing
    price: Mapped[int] = mapped_column(Integer)
    admin_fee: Mapped[Optional[int]] = mapped_column("admin_fee", Integer, nullable=True)

    # Property details
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    parking_spaces: Mapped[int] = mapped_column("parking_spaces", Integer)
    area: Mapped[float] = mapped_column(Float)
    estrato: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_floors: Mapped[Optional[int]] = mapped_column("total_floors", Integer, nullable=True)
    building_age: Mapped[Optional[int]] = mapped_column("building_age", Integer, nullable=True)
    property_condition: Mapped[Optional[str]] = mapped_column("property_condition", String, nullable=True)

    # Location
    address: Mapped[str] = mapped_column(String)
    neighborhood: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    # Media & amenities
    images: Mapped[List[str]] = mapped_column(JSON)
    amenities: Mapped[List[str]] = mapped_column(JSON)

    # Metadata
    first_seen_at: Mapped[datetime] = mapped_column("first_seen_at", DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column("last_seen_at", DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column("is_active", Boolean, default=True)
    content_hash: Mapped[str] = mapped_column("content_hash", String)
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime(timezone=True))


class PriceHistory(Base):
    """Price history for tracking listing price changes."""
    __tablename__ = "price_history"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    listing_id: Mapped[str] = mapped_column("listing_id", String)
    price: Mapped[int] = mapped_column(Integer)
    admin_fee: Mapped[Optional[int]] = mapped_column("admin_fee", Integer, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column("recorded_at", DateTime(timezone=True))
