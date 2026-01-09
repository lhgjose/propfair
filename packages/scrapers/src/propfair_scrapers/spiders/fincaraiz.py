import scrapy
import re
from typing import Optional
from propfair_scrapers.items import ListingItem


class FincaRaizSpider(scrapy.Spider):
    """
    Spider for scraping rental apartment listings from FincaRaiz.

    Site Structure (as of 2026-01-09):
    - Search page: Listing cards with class .listingCard
    - Detail page URL format: /apartamento-en-arriendo-en-{neighborhood}-bogota/{external_id}
    - Price format: "$ 6.500.000" (dots as thousand separators)
    - Admin fee: "+ $ 1.300.000 administración"
    - Property features shown with text like "3 Habs.", "3 Baños", "169 m²"
    - External ID in text: "Código Fincaraíz: 193248980"
    """

    name = "fincaraiz"
    allowed_domains = ["fincaraiz.com.co"]
    start_urls = [
        "https://www.fincaraiz.com.co/arriendo/apartamentos/bogota"
    ]

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "CLOSESPIDER_PAGECOUNT": 3,  # Limit to 3 pages for testing
        "LOG_LEVEL": "INFO",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_page(self, response):
        """Parse search results page to extract listing links."""
        page = response.meta["playwright_page"]

        # Wait for listings to load
        try:
            await page.wait_for_selector(".listingCard", timeout=5000)
        except Exception as e:
            self.logger.error(f"Timeout waiting for listings: {e}")

        await page.close()

        # Extract listing links from cards
        # Links are within .listingCard elements, href contains "/apartamento-en-arriendo" or similar
        listing_links = response.css('.listingCard a[href*="/apartamento-en-arriendo"]::attr(href)').getall()

        # Deduplicate links (some listings may have multiple links to the same page)
        listing_links = list(dict.fromkeys(listing_links))

        self.logger.info(f"Found {len(listing_links)} listings on page")

        for link in listing_links:
            yield response.follow(
                link,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_detail,
            )

        # Pagination - look for next page link
        # Note: Pagination structure may need adjustment based on actual site
        next_page = response.css('a[rel="next"]::attr(href), button[aria-label="Next"]::attr(href)').get()
        if next_page:
            self.logger.info(f"Following pagination to: {next_page}")
            yield response.follow(
                next_page,
                meta={"playwright": True, "playwright_include_page": True},
                callback=self.parse_listing_page,
            )

    async def parse_listing_detail(self, response):
        """Parse individual listing detail page."""
        page = response.meta["playwright_page"]

        # Wait for key elements to load
        try:
            await page.wait_for_selector("h1", timeout=5000)
        except Exception as e:
            self.logger.error(f"Timeout waiting for listing details: {e}")

        await page.close()

        # Extract external ID from URL
        # URL format: /apartamento-en-arriendo-en-chico-navarra-bogota/193248980
        external_id = response.url.split("/")[-1]

        # Extract external ID from page content as backup
        # Text like "Código Fincaraíz: 193248980"
        codigo_text = response.css('*:contains("Código Fincaraíz:")::text').re(r'Código Fincaraíz:\s*(\d+)')
        if codigo_text:
            external_id = codigo_text[0]

        # Price extraction
        # Format: "$ 6.500.000"
        price_text = response.css('p:contains("Precio de Arriendo")::text, p:contains("$")::text').re(r'\$\s*[\d.]+')[0] if response.css('p:contains("$")::text') else None
        price = self._parse_price(price_text) if price_text else None

        # Admin fee extraction
        # Format: "+ $ 1.300.000 administración"
        admin_fee_text = response.css('*:contains("administración")::text').re(r'\$\s*[\d.]+')
        admin_fee = self._parse_price(admin_fee_text[0]) if admin_fee_text else None

        # Title
        # h1 element with format like "Apartamento en Arriendo en Chicó Navarra, Bogotá"
        title = response.css('h1::text').get()

        # Description
        # Multiple text nodes in description section
        description_parts = response.css('h4:contains("Descripción") ~ * ::text').getall()
        description = " ".join([p.strip() for p in description_parts if p.strip()])[:1000]  # Limit to 1000 chars

        # Property features - extract from text like "3 Habs.", "3 Baños", "169 m²"
        bedrooms = self._extract_number_from_text(response, r'(\d+)\s*Habs?\.?')
        bathrooms = self._extract_number_from_text(response, r'(\d+)\s*Baños?\.?')
        parking = self._extract_number_from_details(response, "Parqueaderos")
        area = self._extract_float_from_text(response, r'(\d+(?:[.,]\d+)?)\s*m²')

        # Location - extract from paragraphs in location section
        location_texts = response.css('h4:contains("Ubicación") ~ p::text').getall()
        neighborhood = location_texts[0].strip() if len(location_texts) > 0 else ""
        # Extract just the neighborhood name (before comma)
        if "," in neighborhood:
            neighborhood = neighborhood.split(",")[0].strip()

        address = neighborhood  # Use neighborhood as address for now

        # Coordinates - look for map element or coordinates in script tags
        # Try to find latitude/longitude in various formats
        lat = None
        lng = None

        # Look in data attributes
        map_elem = response.css('[data-lat], [data-lng]')
        if map_elem:
            lat = map_elem.css('::attr(data-lat)').get()
            lng = map_elem.css('::attr(data-lng)').get()

        # Convert to float or use Bogotá center as default
        latitude = float(lat) if lat else 4.6097
        longitude = float(lng) if lng else -74.0817

        # Additional property details from details section
        estrato = self._extract_number_from_details(response, "Estrato")
        floor = self._extract_number_from_details(response, "Piso N")

        # Try to extract building age
        antiguedad_text = self._extract_detail_value(response, "Antigüedad")
        building_age = self._parse_building_age(antiguedad_text)

        # Images - extract from gallery
        # Images are in elements like img within .emblaGalleryCarousel or similar
        images = response.css('.emblaGalleryCarousel img::attr(src), .gallery-image img::attr(src)').getall()
        # Filter out very small images (icons, etc.) and take unique URLs
        images = list(dict.fromkeys([img for img in images if 'cdn' in img and 'logo' not in img.lower()]))[:20]

        # Amenities - extract from comodidades section
        amenities = response.css('h4:contains("Comodidades") ~ * *:contains("•")::text').getall()
        amenities = [a.replace("•", "").strip() for a in amenities if a.strip() and len(a.strip()) > 2]

        # Validate required fields
        if not all([external_id, price, bedrooms is not None, bathrooms is not None, area, neighborhood]):
            self.logger.warning(f"Skipping listing {response.url}: missing required fields")
            self.logger.warning(f"  external_id={external_id}, price={price}, bedrooms={bedrooms}, bathrooms={bathrooms}, area={area}, neighborhood={neighborhood}")
            return

        yield ListingItem(
            external_id=str(external_id),
            source="fincaraiz",
            url=response.url,
            title=title.strip() if title else "",
            description=description.strip() if description else None,
            price=price,
            admin_fee=admin_fee,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            parking_spaces=parking or 0,
            area=area,
            estrato=estrato,
            floor=floor,
            building_age=building_age,
            address=address,
            neighborhood=neighborhood,
            city="Bogotá",
            latitude=latitude,
            longitude=longitude,
            images=images,
            amenities=amenities,
        )

    def _parse_price(self, text: str) -> Optional[int]:
        """Parse Colombian peso price format."""
        if not text:
            return None
        # Remove $ and separators: "$ 2.500.000" -> 2500000
        cleaned = text.replace("$", "").replace(".", "").replace(",", "").strip()
        try:
            return int(cleaned)
        except ValueError:
            self.logger.warning(f"Could not parse price: {text}")
            return None

    def _extract_number_from_text(self, response, pattern: str) -> Optional[int]:
        """Extract number using regex pattern from page text."""
        matches = response.css('*::text').re(pattern)
        if matches:
            try:
                return int(matches[0])
            except ValueError:
                pass
        return None

    def _extract_float_from_text(self, response, pattern: str) -> Optional[float]:
        """Extract float using regex pattern from page text."""
        matches = response.css('*::text').re(pattern)
        if matches:
            try:
                # Handle both comma and period as decimal separator
                value = matches[0].replace(",", ".")
                return float(value)
            except ValueError:
                pass
        return None

    def _extract_number_from_details(self, response, label: str) -> Optional[int]:
        """Extract number from property details section."""
        # Details are in format: bullet • Label / Value
        # Look for the label, then get the next strong element
        detail_text = response.css(f'*:contains("{label}") ~ *::text, *:contains("{label}") + *::text').re(r'(\d+)')
        if detail_text:
            try:
                return int(detail_text[0])
            except ValueError:
                pass
        return None

    def _extract_detail_value(self, response, label: str) -> Optional[str]:
        """Extract text value from property details section."""
        # Get text following the label
        values = response.css(f'*:contains("{label}") ~ strong::text, *:contains("{label}") + strong::text').getall()
        if values:
            return values[0].strip()
        return None

    def _parse_building_age(self, text: Optional[str]) -> Optional[int]:
        """Parse building age from text like 'más de 30 años' or '5 años'."""
        if not text:
            return None

        # Extract numbers from text
        numbers = re.findall(r'\d+', text)
        if numbers:
            try:
                return int(numbers[0])
            except ValueError:
                pass
        return None
