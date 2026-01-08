import pytest
from propfair_scrapers.spiders.fincaraiz import FincaRaizSpider


def test_spider_name():
    spider = FincaRaizSpider()
    assert spider.name == "fincaraiz"


def test_spider_allowed_domains():
    spider = FincaRaizSpider()
    assert "fincaraiz.com.co" in spider.allowed_domains


def test_spider_start_urls():
    spider = FincaRaizSpider()
    assert len(spider.start_urls) > 0
    assert "bogota" in spider.start_urls[0].lower()
