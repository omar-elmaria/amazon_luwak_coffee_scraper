import scrapy
from amazon_luwak_coffee.items import AmazonLuwakCoffeeItem
from scrapy.loader import ItemLoader
from dotenv import load_dotenv
from scraper_api import ScraperAPIClient
import os
import datetime as dt

# Load the environment variables
load_dotenv()

# Scraper API for rotating through proxies
client = ScraperAPIClient(os.getenv("SCRAPER_API_KEY"))

class LuwakCoffeeSpider(scrapy.Spider):
    name = "luwak_coffee_spider"
    allowed_domains = ["amazon.de"]
    custom_settings = {
        "FEEDS":{"product_info.json":{"format": "json", "overwrite": True}}, # Export to a JSON file with an overwrite functionality
        "FEED_EXPORT_ENCODING": "utf-8", # UTF-8 deals with all types of characters
        "RETRY_TIMES": 3, # Retry failed requests up to 3 times
        "CONCURRENT_REQUESTS": 5, # The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader
        "DOWNLOAD_TIMEOUT": 60 # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
    }

    def start_requests(self):
        # Landing page of the Luwak coffee category on Amazon
        url = "https://www.amazon.de/s?k=luwak+kaffee&__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2I075LUJM396D&sprefix=luwak+kaffee%2Caps%2C97&ref=nb_sb_noss_1"
        yield scrapy.Request(client.scrapyGet(url = url, country_code = "de"), callback = self.parse)

    # Define a function to parse the responses from "start_requests"
    def parse(self, response):
        products = response.css("div[data-component-type = s-search-result]")
        for item in products:
            # Go to the product page that was scrapped from the landing page and send a scrapy request via the API to load the content of that page
            yield scrapy.Request(
                client.scrapyGet(url = "https://www.amazon.de" + item.css("a.a-link-normal.s-no-outline::attr(href)").get(), country_code = "de"),
                callback = self.parse_product, # Use the parse_product function to scrape the content of the product page
                dont_filter = True
            )
        
        # The landing page has multiple pages. Add a pagination logic to go through all pages
        next_page = response.xpath("//a[contains(@class, 's-pagination-next')]/@href").get()
        if next_page is not None:
            yield scrapy.Request(client.scrapyGet(url = "https://www.amazon.de" + next_page, country_code = "de"), callback = self.parse, dont_filter = True)
    
    def parse_product(self, response):
        ppd = response.css("div[id = 'ppd']")
        if len(ppd) == 0: # if the returned response is an empty list...
            ppd = response.css("div[id = 'ppdHandmade']") # Some product pages have this selector instead of "ppd"
        else:
            pass
        
        prod = ItemLoader(item = AmazonLuwakCoffeeItem(), selector = ppd)
        # Product name
        prod.add_css("product_name", "span[id = productTitle]")

        # Main image link
        prod.add_css("main_image_link", "span.a-button-text img::attr(src)")
        
        # Price
        price_check = ppd.css("span[id = sns-base-price]::text").get()
        prod.add_css("price", "span[id = sns-base-price]") if price_check is not None else prod.add_css("price", "span[class = a-offscreen]")
        
        # Vendor data
        prod.add_css("vendor_name", "a[id = bylineInfo]")
        prod.add_css("vendor_link", "a[id = bylineInfo]::attr(href)")
        
        # Reviews
        overall_reviews_out_of_5_check = ppd.css("span.a-icon-alt::text").get()
        num_reviews_check = ppd.css("span[id = acrCustomerReviewText]::text").get()
        pct_5_star_reviews_check = ppd.xpath("//a[contains(@title, 'der Rezensionen haben 5 Sterne')]/@title").get()
        pct_4_star_reviews_check = ppd.xpath("//a[contains(@title, 'der Rezensionen haben 4 Sterne')]/@title").get()
        pct_3_star_reviews_check = ppd.xpath("//a[contains(@title, 'der Rezensionen haben 3 Sterne')]/@title").get()
        pct_2_star_reviews_check = ppd.xpath("//a[contains(@title, 'der Rezensionen haben 2 Sterne')]/@title").get()
        pct_1_star_reviews_check = ppd.xpath("//a[contains(@title, 'der Rezensionen haben 1 Sterne')]/@title").get()

        prod.add_css("overall_reviews_out_of_5", "span.a-icon-alt") if overall_reviews_out_of_5_check is not None else prod.add_value("overall_reviews_out_of_5", "NA")
        prod.add_css("num_reviews", "span[id = acrCustomerReviewText]") if num_reviews_check is not None else prod.add_value("num_reviews", "0")
        prod.add_xpath("pct_5_star_reviews", "//a[contains(@title, 'der Rezensionen haben 5 Sterne')]/@title") if pct_5_star_reviews_check is not None else prod.add_value("pct_5_star_reviews", "0%")
        prod.add_xpath("pct_4_star_reviews", "//a[contains(@title, 'der Rezensionen haben 4 Sterne')]/@title") if pct_4_star_reviews_check is not None else prod.add_value("pct_4_star_reviews", "0%")
        prod.add_xpath("pct_3_star_reviews", "//a[contains(@title, 'der Rezensionen haben 3 Sterne')]/@title") if pct_3_star_reviews_check is not None else prod.add_value("pct_3_star_reviews", "0%")
        prod.add_xpath("pct_2_star_reviews", "//a[contains(@title, 'der Rezensionen haben 2 Sterne')]/@title") if pct_2_star_reviews_check is not None else prod.add_value("pct_2_star_reviews", "0%")
        prod.add_xpath("pct_1_star_reviews", "//a[contains(@title, 'der Rezensionen haben 1 Sterne')]/@title") if pct_1_star_reviews_check is not None else prod.add_value("pct_1_star_reviews", "0%")
        
        # Product link
        try:
            prod.add_value("product_link", response.headers['Sa-Final-Url'])
        except KeyError:
            prod.add_value("product_link", "None")

        # Extraction timestamp
        prod.add_value("extraction_timestamp", dt.datetime.now())
        
        yield prod.load_item()