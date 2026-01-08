import scrapy


class ListingItem(scrapy.Item):
    # Required fields
    external_id = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    parking_spaces = scrapy.Field()
    area = scrapy.Field()
    address = scrapy.Field()
    neighborhood = scrapy.Field()
    city = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()

    # Optional fields
    description = scrapy.Field()
    admin_fee = scrapy.Field()
    estrato = scrapy.Field()
    floor = scrapy.Field()
    total_floors = scrapy.Field()
    building_age = scrapy.Field()
    property_condition = scrapy.Field()
    images = scrapy.Field()
    amenities = scrapy.Field()
