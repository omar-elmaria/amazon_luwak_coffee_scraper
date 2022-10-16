# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Compose
from w3lib.html import remove_tags
import re

# Define a function to extract the price from the price tag without the Euro sign
def price_regex(price):
    return re.findall("[0-9]+,[0-9]+", price) # Extract the price from the extracted tag without the Euro sign

# Define a function to replace the "," in the price with a dot
def price_formatter(price):
    return float(price.replace(",", ".")) # Replace the "," in the price with a dot

# Define a function to extract the vendor name from the subtitle
def vendor_name_regex(string):
    return re.findall("(?<=Marke:\s)\w.*|(?<=Besuche den\s)\w.*", string) # Match anything after "Marke: " or "Besuche den "

# Define a function to extract the link to the vendor's page on Amazon from the subtitle
def vendor_link_prefix(string):
    return "https://www.amazon.de" + string # Append the "https://www.amazon.de" prefix to the extracted vendor link

# Define a function to extract the overall review value of of 5 stars
def overall_reviews_regex(string):
    if string == "NA":
        return "NA"
    else:
        return re.findall("(\d{1},\d{1})", string)

# Define a function to extract the total number of reviews for the product
def num_reviews_regex(string):
    if string == "NA":
        return "NA"
    else:
        return re.findall("\d", string) # Return the numeric part only from the string (e.g., return 20 from '20 Sternebewertungen')

# Define a function to extract the percentage of 5 star, 4 star, 3 star, 2 star, and 1 star reviews
def pct_reviews_regex(string):
    return re.findall("\d+%", string) # Extract the percentage from the extracted attribute and replace the % with nothing so that you end up with a number

# Define a function to replace the % sign in the field above by nothing so that it can be displayed as a number
def pct_reviews_formatter(string):
    return string.replace("%", "")

class AmazonLuwakCoffeeItem(scrapy.Item):
    # define the fields for your item here like:
    
    # Product name
    product_name = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    
    # Main image link
    main_image_link = scrapy.Field(output_processor = TakeFirst())

    # Price
    price = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip, price_regex, price_formatter), output_processor = TakeFirst())
    
    # Vendor data
    vendor_name = scrapy.Field(input_processor = MapCompose(remove_tags, vendor_name_regex), output_processor = TakeFirst())
    vendor_link = scrapy.Field(input_processor = MapCompose(vendor_link_prefix), output_processor = TakeFirst())
    
    # Reviews
    overall_reviews_out_of_5 = scrapy.Field(input_processor = MapCompose(remove_tags, overall_reviews_regex), output_processor = Compose(TakeFirst(), lambda x: str.replace(x, ",", ".")))
    num_reviews = scrapy.Field(input_processor = MapCompose(remove_tags, num_reviews_regex), output_processor = Compose(TakeFirst(), int))
    pct_5_star_reviews = scrapy.Field(input_processor = MapCompose(pct_reviews_regex), output_processor = Compose(TakeFirst(), pct_reviews_formatter, int))
    pct_4_star_reviews = scrapy.Field(input_processor = MapCompose(pct_reviews_regex), output_processor = Compose(TakeFirst(), pct_reviews_formatter, int))
    pct_3_star_reviews = scrapy.Field(input_processor = MapCompose(pct_reviews_regex), output_processor = Compose(TakeFirst(), pct_reviews_formatter, int))
    pct_2_star_reviews = scrapy.Field(input_processor = MapCompose(pct_reviews_regex), output_processor = Compose(TakeFirst(), pct_reviews_formatter, int))
    pct_1_star_reviews = scrapy.Field(input_processor = MapCompose(pct_reviews_regex), output_processor = Compose(TakeFirst(), pct_reviews_formatter, int))
    
    # Product link
    product_link = scrapy.Field(input_processor = MapCompose(remove_tags, str.strip), output_processor = TakeFirst())
    
    # Extraction timestamp
    extraction_timestamp = scrapy.Field()
