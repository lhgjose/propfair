import scrapy
from propfair_scrapers.items import ListingItem


class FincaRaizSpider(scrapy.Spider):
    name = "fincaraiz"
    allowed_domains = ["fincaraiz.com.co"]
    start_urls = [
        "https://www.fincaraiz.com.co/apartamentos/arriendo/bogota/"
    ]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_page(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        # Extract listing links
        listing_links = response.css("a.card-result-image::attr(href)").getall()

        for link in listing_links:
            yield response.follow(
                link,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_detail,
            )

        # Pagination
        next_page = response.css("a.pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(
                next_page,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_detail(self, response):
        page = response.meta["playwright_page"]
        await page.close()

        # Extract external ID from URL
        external_id = response.url.split("/")[-1].split("-")[-1]

        # Price extraction
        price_text = response.css("span.price::text").get()
        price = self._parse_price(price_text) if price_text else None

        # Basic info
        title = response.css("h1.title::text").get()
        description = response.css("div.description p::text").get()

        # Property details
        bedrooms = self._extract_number(response, "habitaciones")
        bathrooms = self._extract_number(response, "baños")
        parking = self._extract_number(response, "garajes")
        area = self._extract_float(response, "área")

        # Location
        neighborhood = response.css("span.neighborhood::text").get()
        address = response.css("span.address::text").get()

        # Coordinates
        lat = response.css("div.map::attr(data-lat)").get()
        lng = response.css("div.map::attr(data-lng)").get()

        # Additional details
        estrato = self._extract_number(response, "estrato")
        admin_fee_text = response.css("span.admin-fee::text").get()
        admin_fee = self._parse_price(admin_fee_text) if admin_fee_text else None

        # Images
        images = response.css("div.gallery img::attr(src)").getall()

        yield ListingItem(
            external_id=external_id,
            source="fincaraiz",
            url=response.url,
            title=title.strip() if title else None,
            description=description.strip() if description else None,
            price=price,
            admin_fee=admin_fee,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking_spaces=parking or 0,
            area=area,
            estrato=estrato,
            address=address.strip() if address else "",
            neighborhood=neighborhood.strip() if neighborhood else "",
            city="Bogotá",
            latitude=float(lat) if lat else 4.6097,
            longitude=float(lng) if lng else -74.0817,
            images=images,
        )

    def _parse_price(self, text: str) -> int | None:
        if not text:
            return None
        # Remove $ and . separators, e.g., "$ 2.500.000" -> 2500000
        cleaned = text.replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            return int(cleaned)
        except ValueError:
            return None

    def _extract_number(self, response, label: str) -> int | None:
        selector = f"span:contains('{label}') + span::text"
        value = response.css(selector).get()
        if value:
            try:
                return int(value.strip())
            except ValueError:
                pass
        return None

    def _extract_float(self, response, label: str) -> float | None:
        selector = f"span:contains('{label}') + span::text"
        value = response.css(selector).get()
        if value:
            cleaned = value.replace("m²", "").replace(",", ".").strip()
            try:
                return float(cleaned)
            except ValueError:
                pass
        return None
