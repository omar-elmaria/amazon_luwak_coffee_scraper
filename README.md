# amazon_luwak_coffee_scraper
This repo contains a Python-based web crawler that scrapes data on Luwak coffee products from amazon.de. It is designed to surpass Amazon's anti-bot mechanisms and crawl the most important info from the product pages successfully

# 1. Objective of the Project
The aim of this project was to scrape the listing page of the Luwak Coffee category on Amazon and crawl the information on the individual product pages that were obtained from the listing page.

**Listing Page**

![image](https://user-images.githubusercontent.com/98691360/198840230-92704ddd-feb9-4f72-9225-389a698187f1.png)

**An Example of a Product Page**

![image](https://user-images.githubusercontent.com/98691360/198840268-a105828b-26c8-4789-ae05-dd55b5f3c741.png)

The data points I chose to extract from the product pages for this project are:
- product_name
- product_url
- main_image_link
- price
- vendor_name
- vendor_url
- overall_reviews_out_of_5
- num_reviews
- pct_5_star_reviews
- pct_4_star_reviews
- pct_3_star_reviews
- pct_2_star_reviews
- pct_1_star_reviews

# 2. Scraping Methodology
I used the ```scrapy``` framework in Python to crawl this information. Amazon is a difficult website to scrape. because it employs many **anti-bot mechanism** that block your IP if you try to crawl it using the standard methods.

To overcome this challenge, I used ```ScraperAPI```, which is a **proxy solution** for web scraping that is designed to make scraping the web at scale as simple as possible. It does that by removing the hassle of finding **high quality proxies**, **rotating proxy pools**, **detecting bans**, **solving CAPTCHAs**, and **managing geotargeting**, and **rendering Javascript**. With simple API calls, you can get the HTML from any web page you desire and scale your requests as needed.

## 2.1 How to Integrate ScraperAPI Into Your Code?
First, you need to create ScraperAPI account. Use the [sign-up page](https://dashboard.scraperapi.com/signup) to do that. ScraperAPI offers a **free plan of 1,000 free API credits** per month (with a maximum of **5 concurrent connections**) for small scraping projects. For the first 7-days after you sign up, you will have access to **5,000 free requests** along with all the premium features to test all capabilities of the API.

After you create your account, you should land on a page that looks like this...

![image](https://user-images.githubusercontent.com/98691360/198832083-12a3bc7e-d8a4-492e-bb61-2f3e93db98ed.png)

Assuming you already cloned the repo via this command ```git clone https://github.com/omar-elmaria/amazon_luwak_coffee_scraper.git```, you should create a ```.env``` file and place your API key in it as shown below.
```
SCRAPER_API_KEY={INSERT_API_KEY_WITHOUT_THE_CURLY_BRACES}
```
When you do that, the spiders should run without problems. To fire up a spider, ```cd``` into the folder ```amazon_luwak_coffee``` and run the following command in your terminal, replacing the variable {SPIDER_NAME} with the name of the spider you want to run.
```
scrapy crawl SPIDER_NAME
```
After the spider finishes its job, a **JSON file** will appear in your directory showing you the results. Depending on the specific spider you run, it will look something like this.

![image](https://user-images.githubusercontent.com/98691360/198840826-99803bc8-7e39-49ea-9389-f243abbf1aab.png)
_N.B. The picture is truncated to preserve space. Not all fields are shown_

# 3. Spider Design
In this project, I created two spiders, ```url_extractor_spider``` and ```luwak_coffee_spider```. The **first one** extracts the links to the product pages from listing page. The **second one** extracts the data we want from the product page.

## 3.1 Scrapy and ScraperAPI Best Practices
Whenever you use ```ScraperAPI```, it is recommended that you add these settings to your spider class. You can check how the dictionary below is added to the spider class by looking at one of the spider Py files.
```python
# Define the dictionary that contains the custom settings of the spiders. This will be used in all other spiders
custom_settings_dict = {
  "FEED_EXPORT_ENCODING": "utf-8", # UTF-8 deals with all types of characters
  "RETRY_TIMES": 10, # Retry failed requests up to 10 times (10 instead of 3 because Fiverr is a hard site to scrape)
  "AUTOTHROTTLE_ENABLED": False, # Disables the AutoThrottle extension (recommended to be used with proxy services unless the website is tough to crawl)
  "RANDOMIZE_DOWNLOAD_DELAY": False, # If enabled, Scrapy will wait a random amount of time (between 0.5 * DOWNLOAD_DELAY and 1.5 * DOWNLOAD_DELAY) while fetching requests from the same website
  "CONCURRENT_REQUESTS": 5, # The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader
  "DOWNLOAD_TIMEOUT": 60, # Setting the timeout parameter to 60 seconds as per the ScraperAPI documentation
  "FEEDS": {"JSON_OUTPUT_FILE_NAME.json":{"format": "json", "overwrite": True}} # Export to a JSON file with an overwrite functionality
}
```

```ScraperAPI``` allows you to use different options in your API calls to customize your requests. Please check the ```Customise API Functionality``` section in the API documentation to see what each of these option means and how it affects your API credits.
- render
- country_code
- premium
- session_number
- keep_headers
- device_type
- autoparse
- ultra_premium

In this project, I used ```country_code``` to send my requests from German IP addresses.

Whenever you send similar requests to a webpage, which is the case we have with this spider, ```Scrapy``` automatically filters out the duplicate ones, which prevents you from crawling all the data you want. To prevent this behavior, you should set the ```dont_filter``` parameter in the ```scrapy.Request``` method to ```True``` like so...
```python
yield scrapy.Request(
  client.scrapyGet(url = url, country_code = "de"),
  callback = self.parse,
  dont_filter = True
)
```

If you want to send information from one parsing function to the next, you can use the ```meta``` parameter in the ```scrapy.Request``` method. An example is shown below.
```python
# Define a function to start the crawling process. This function takes the URLs from cat_page_urls_list
url = "https://www.amazon.de/Tesdorpfs-100-Luwak-Kaffee-Kaffeespezialit%C3%A4t/dp/B08HW1B69H"
def start_requests(self):
  yield scrapy.Request(
    client.scrapyGet(url = url, country_code = "de"),
    callback = self.parse,
    dont_filter = True, # This is important so that scrapy does not filter out similar requests. We want all requests to be sent
    meta = dict(master_url = url) # The meta parameter sends the URL to the parse function and you can access it by typing response.meta["master_url"]
  )
```

If you want to run your spiders as a script and **not** from the terminal, use the code below.
```python
from scrapy.crawler import CrawlerProcess

class TestSpider(scrapy.Spider):
  # Some code goes here...

process = CrawlerProcess() # You can also insert custom settings as a dictionary --> CrawlerProcess(settings={"CONCURRENT_REQUESTS": 5}) 
process.crawl(TestSpider)
process.start()
```

# 4. Output of the Code
The code produces **two JSON files**, ```pdp_urls.json``` and ```product_info.json```. There is also a notebook file called ```product_info.ipynb```, which parses the data in the JSONs, merges it, and and places it in a pandas dataframe.

# 5. Questions?
If you have any questions or wish to build a scraper for a particular use case (e.g., Competitive Intelligence), feel free to contact me on [LinkedIn](https://www.linkedin.com/in/omar-elmaria/)
