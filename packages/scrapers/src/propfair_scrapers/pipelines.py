import hashlib
import json
from scrapy.exceptions import DropItem


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
    def process_item(self, item, spider):
        # Will be implemented when DB connection is ready
        return item
