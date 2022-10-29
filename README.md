# amazon_luwak_coffee_scraper
This repo contains a Python-based web crawler that scrapes data on Luwak coffee products from amazon.de. It is designed to surpass Amazon's anti-bot mechanisms and crawl the most important info from the product pages successfully

# 1. Objective of the Project
The aim of this project was to scrape the **home page**, **category pages**, and **individual product pages** of this online furniture website [Kemitt](https://kemitt.com/en-eg/)

**Home Page**

![image](https://user-images.githubusercontent.com/98691360/198837087-2fdfb167-9a28-401f-9ad9-7eab8ce5e045.png)

**Category Page**

![image](https://user-images.githubusercontent.com/98691360/198837196-80f83368-542e-488e-ac73-80984ffd6f4d.png)

**Individual Product Page**

![image](https://user-images.githubusercontent.com/98691360/198837297-1b757811-a118-4f7f-9295-854de1549c6a.png)

The spider follows a **sequence** when crawling these website sections (Home Page --> Category Page --> Product Page) because one section leads to the other. The information that could be extracted from the scraping process are:
- product_name
- product_url
- category_name
- category_url
- supplier_name
- supplier_url
- strikethrough_price
- current_price
- promised_delivery_time_in_days
- main_image_url
- page_rank_of_product
- last_page_of_category

# 2. Scraping Methodology
I used the ```scrapy``` framework in Python to crawl this information from **two categories**, **"Tables"** and **"Bedroom"**. Kemitt is a difficult website to scrape. because it employs many **anti-bot mechanism** that block your IP if you try to crawl it using the standard methods. Moreover, it is **Javascript-rendered**, which means that the data you want to crawl is **not** present in the HTML code that can be obtained by a standard ```GET``` request.

To overcome these two challenges, I used ```ScraperAPI```, which is a **proxy solution** for web scraping that is designed to make scraping the web at scale as simple as possible. It does that by removing the hassle of finding **high quality proxies**, **rotating proxy pools**, **detecting bans**, **solving CAPTCHAs**, and **managing geotargeting**, and **rendering Javascript**. With simple API calls, you can get the HTML from any web page you desire and scale your requests as needed.

## 2.1 How to Integrate ScraperAPI Into Your Code?
First, you need to create ScraperAPI account. Use the [sign-up page](https://dashboard.scraperapi.com/signup) to do that. ScraperAPI offers a **free plan of 1,000 free API credits** per month (with a maximum of **5 concurrent connections**) for small scraping projects. For the first 7-days after you sign up, you will have access to **5,000 free requests** along with all the premium features to test all capabilities of the API.

After you create your account, you should land on a page that looks like this...

![image](https://user-images.githubusercontent.com/98691360/198832083-12a3bc7e-d8a4-492e-bb61-2f3e93db98ed.png)

Assuming you already cloned the repo via this command ```git clone https://github.com/omar-elmaria/ecommerce_furniture_website_scraper.git```, you should create a ```.env``` file and place your API key in it as shown below.
```
SCRAPER_API_KEY={INSERT_API_KEY_WITHOUT_THE_CURLY_BRACES}
```
When you do that, the spiders should run without problems. To fire up a spider, ```cd``` into the folder ```furniture_ecomm``` and run the following command in your terminal, replacing the variable {SPIDER_NAME} with the name of the spider you want to run.
```
scrapy crawl SPIDER_NAME
```
After the spider finishes its job, a **JSON file** will appear in your directory showing you the results. Depending on the specific spider you run, it will look something like this.

![image](https://user-images.githubusercontent.com/98691360/198837742-d4807871-0590-4f89-857c-fecaa9238d40.png)
_N.B. The picture is truncated to preserve space. Not all fields are shown_

# 3. Spider Design
In this project, I created four spiders, ```home_page_spider```, ```cat_page_spider_std_pagination_logic```, ```cat_page_spider_async_pagination_logic```, and ```prod_page_spider```. The names of the spiders indicate which section of the website they crawl. 

**Why are there two spiders for the category page sectoion?**
The first one utilizes the standard logic suggested by the scrapy documentation to crawl **paginated websites**. It works by obtaining the **link to the next page** via a **CSS or XPATH selector** and sending a ```scrapy.Request``` with a **callback function** to crawl the next page with the same parsing function used for the first page.

The problem with this logic is that it **kills concurrency** because you need to wait for one page to be rendered and crawled before you can send a request to the next page and crawl it. That's where the second spider ```cat_page_spider_async_pagination_logic``` comes in. It sends requests to **all** the pages that I want to crawl **asynchronously** and parses the data whenever it receives back a response from Kemitt's server. I recommend you use that spider because it is 5 to 7 times faster than the other one.

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

In this project, I use ```render``` to render the Javascript content of Kemitt and ```country_code``` to send my requests from German IP addresses.

Whenever you send similar requests to a webpage, which is the case we have with this spider, ```Scrapy``` automatically filters out the duplicate ones, which prevents you from crawling all the data you want. To prevent this behavior, you should set the ```dont_filter``` parameter in the ```scrapy.Request``` method to ```True``` like so...
```python
yield scrapy.Request(
  client.scrapyGet(url = url, country_code = "de", render = True),
  callback = self.parse,
  dont_filter = True
)
```

If you want to send information from one parsing function to the next, you can use the ```meta``` parameter in the ```scrapy.Request``` method. An example is shown below.
```python
# Define a function to start the crawling process. This function takes the URLs from cat_page_urls_list
url = "https://kemitt.com/en-eg/"
def start_requests(self):
  yield scrapy.Request(
    client.scrapyGet(url = url, country_code = "de", render = True),
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
The code produces **three JSON files**, ```home_page.json```, ```cat_page.json```, and ```prod_page.json```. There is also a notebook file called ```combine_jsons.ipynb```, which parses the data in the JSONs and places it in a pandas dataframe.

# 5. Questions?
If you have any questions or wish to build a scraper for a particular use case (e.g., Competitive Intelligence), feel free to contact me on [LinkedIn](https://www.linkedin.com/in/omar-elmaria/)
