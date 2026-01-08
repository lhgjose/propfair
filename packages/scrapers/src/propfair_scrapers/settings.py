BOT_NAME = "propfair_scrapers"

SPIDER_MODULES = ["propfair_scrapers.spiders"]
NEWSPIDER_MODULE = "propfair_scrapers.spiders"

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

ITEM_PIPELINES = {
    "propfair_scrapers.pipelines.ValidationPipeline": 100,
    "propfair_scrapers.pipelines.DeduplicationPipeline": 200,
    "propfair_scrapers.pipelines.DatabasePipeline": 300,
}

LOG_LEVEL = "INFO"
