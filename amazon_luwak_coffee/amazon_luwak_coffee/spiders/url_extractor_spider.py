import scrapy
from dotenv import load_dotenv
from scraper_api import ScraperAPIClient
import os

# Load the environment variables
load_dotenv()

# Scraper API for rotating through proxies
client = ScraperAPIClient(os.getenv('SCRAPER_API_KEY'))

class UrlExtractorSpider(scrapy.Spider):
    name = 'url_extractor_spider'
    allowed_domains = ['amazon.de']
    custom_settings = {
        "FEEDS":{"pdp_urls.json":{"format": "json", "overwrite": True}},
        "FEED_EXPORT_ENCODING": "utf-8",
        "RETRY_TIMES": 5,
        "DOWNLOAD_TIMEOUT": 60 # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
    }

    def start_requests(self):
        first_url = "https://www.amazon.de/s?k=luwak+kaffee&__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2I075LUJM396D&sprefix=luwak+kaffee%2Caps%2C97&ref=nb_sb_noss_1"
        yield scrapy.Request(client.scrapyGet(url = first_url, country_code = "de"), callback = self.parse)

    def parse(self, response):
        pdp_urls = response.css("div[data-component-type = 's-search-result']")
        for item in pdp_urls:
            yield {
                "url": "https://www.amazon.de" + item.css("a.a-link-normal.s-no-outline::attr(href)").get()
            }
        
        next_page = response.xpath("//a[contains(@class, 's-pagination-next')]/@href").get()
        if next_page is not None:
            yield scrapy.Request(client.scrapyGet(url = "https://www.amazon.de" + next_page, country_code = "de"), callback = self.parse, dont_filter = True)
