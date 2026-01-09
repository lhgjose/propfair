import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add API models to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../api/src"))

# Deferred import to avoid issues in test environments
try:
    from propfair_api.models import Listing, PriceHistory
except ImportError:
    # Will be imported when needed
    Listing = None
    PriceHistory = None


class ValidationPipeline:
    REQUIRED_FIELDS = [
        "external_id",
        "source",
        "url",
        "title",
        "price",
        "bedrooms",
        "bathrooms",
        "parking_spaces",
        "area",
        "address",
        "neighborhood",
        "city",
        "latitude",
        "longitude",
    ]

    def process_item(self, item, spider):
        for field in self.REQUIRED_FIELDS:
            if field not in item or item[field] is None:
                raise DropItem(f"Missing required field: {field}")

        if item["price"] <= 0:
            raise DropItem(f"Invalid price: {item['price']}")

        if item["area"] <= 0:
            raise DropItem(f"Invalid area: {item['area']}")

        return item


class DeduplicationPipeline:
    def __init__(self):
        self.seen_hashes = set()

    def process_item(self, item, spider):
        content = {
            "external_id": item["external_id"],
            "source": item["source"],
            "price": item["price"],
            "title": item["title"],
        }
        content_hash = hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()

        if content_hash in self.seen_hashes:
            raise DropItem(f"Duplicate item: {item['external_id']}")

        self.seen_hashes.add(content_hash)
        item["content_hash"] = content_hash
        return item


class DatabasePipeline:
    """Pipeline to save listings to PostgreSQL database."""

    def __init__(self):
        self.engine = None
        self.Session = None

    def open_spider(self, spider):
        """Initialize database connection when spider opens."""
        # Try importing models if not already imported
        global Listing, PriceHistory
        if Listing is None or PriceHistory is None:
            try:
                from propfair_api.models import Listing as L, PriceHistory as PH
                Listing = L
                PriceHistory = PH
            except ImportError as e:
                spider.logger.error(f"Could not import models: {e}")
                return

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            spider.logger.error("DATABASE_URL not set, database pipeline disabled")
            return

        try:
            self.engine = create_engine(database_url, pool_pre_ping=True)
            self.Session = sessionmaker(bind=self.engine)
            spider.logger.info("Database connection established")
        except Exception as e:
            spider.logger.error(f"Failed to connect to database: {e}")

    def close_spider(self, spider):
        """Close database connection when spider closes."""
        if self.engine:
            self.engine.dispose()
            spider.logger.info("Database connection closed")

    def process_item(self, item, spider):
        """Save or update listing in database."""
        if not self.Session:
            spider.logger.warning("Database not connected, skipping item")
            return item

        session = self.Session()
        try:
            # Check if listing exists
            existing = session.query(Listing).filter_by(
                source=item["source"],
                external_id=item["external_id"]
            ).first()

            if existing:
                self._update_listing(session, existing, item, spider)
            else:
                self._create_listing(session, item, spider)

            session.commit()
            spider.logger.debug(f"Saved listing: {item['external_id']}")

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Failed to save listing {item['external_id']}: {e}")
        finally:
            session.close()

        return item

    def _generate_cuid(self) -> str:
        """Generate a CUID-like ID."""
        import secrets
        timestamp = hex(int(datetime.now(timezone.utc).timestamp() * 1000))[2:]
        random_part = secrets.token_hex(8)
        return f"c{timestamp}{random_part}"

    def _create_listing(self, session, item, spider):
        """Create a new listing in the database."""
        listing = Listing(
            id=self._generate_cuid(),
            external_id=item["external_id"],
            source=item["source"],
            url=item["url"],
            title=item["title"],
            description=item.get("description"),
            price=item["price"],
            admin_fee=item.get("admin_fee"),
            bedrooms=item["bedrooms"],
            bathrooms=item["bathrooms"],
            parking_spaces=item["parking_spaces"],
            area=item["area"],
            estrato=item.get("estrato"),
            floor=item.get("floor"),
            total_floors=item.get("total_floors"),
            building_age=item.get("building_age"),
            property_condition=item.get("property_condition"),
            address=item["address"],
            neighborhood=item["neighborhood"],
            city=item["city"],
            latitude=item["latitude"],
            longitude=item["longitude"],
            images=item.get("images", []),
            amenities=item.get("amenities", []),
            first_seen_at=datetime.now(timezone.utc),
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
            content_hash=item["content_hash"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(listing)
        spider.logger.info(f"Created new listing: {item['external_id']}")

    def _update_listing(self, session, existing, item, spider):
        """Update an existing listing in the database."""
        # Update last_seen_at
        existing.last_seen_at = datetime.now(timezone.utc)
        existing.updated_at = datetime.now(timezone.utc)

        # Check if price changed
        if existing.price != item["price"]:
            spider.logger.info(
                f"Price change detected for {item['external_id']}: "
                f"{existing.price} → {item['price']}"
            )

            # Create price history record
            price_history = PriceHistory(
                id=self._generate_cuid(),
                listing_id=existing.id,
                price=item["price"],
                admin_fee=item.get("admin_fee"),
                recorded_at=datetime.now(timezone.utc)
            )
            session.add(price_history)

            # Update listing price
            existing.price = item["price"]
            existing.admin_fee = item.get("admin_fee")

        # Update other fields that might change
        existing.title = item["title"]
        existing.description = item.get("description")
        existing.images = item.get("images", [])
        existing.amenities = item.get("amenities", [])
        existing.content_hash = item["content_hash"]

        spider.logger.info(f"Updated existing listing: {item['external_id']}")
