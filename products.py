#!/usr/bin/python3

import logging
from os.path import devnull


import time 
import datetime


from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver 
from selenium.webdriver import Firefox 
from selenium.webdriver.firefox.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.firefox import GeckoDriverManager

logger = logging.getLogger()


HOME_URL =  "https://tienda.mercadona.es/categories/"


headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


options = webdriver.FirefoxOptions()
options.add_argument('--headless')

# path web driver downloaded
firefox_path = GeckoDriverManager().install()
firefox_service = Service(firefox_path, log_path=devnull)

# defined options
driver = Firefox(options=options, service=firefox_service)
driver.implicitly_wait(3)

# get url and wait
driver.get(HOME_URL)


def get_category_products(category_urls):

    product_list = []
    # TIMESTAMP
    unixtime = time.time()
    timestamp = datetime.datetime.fromtimestamp(unixtime).date()
    num_urls = 1

    for url in category_urls:

        logger.debug(f"Currently scraping {url}")
        driver.get(url)
        time.sleep(2)
     
        existSubcategory = True
        num_urls = 1
        while existSubcategory:
            num_urls += 1        
            # CATEGORY
            try: 
                category = driver.find_element(By.CLASS_NAME, 'category-detail__title').text
                
            except Exception as e:
                logger.info("Category not found")
                logger.exception(e)

            # PRODUCT DATA
            products = driver.find_elements(By.CLASS_NAME, 'product-cell')
            for product in products:

                # NAME
                try: 
                    name = product.find_element(By.XPATH, './button/div[2]/h4').text
                except Exception as e:
                    logger.error("Product name not found")
                    logger.exception(e)

                # FORMAT
                try:
                    format = product.find_element(By.XPATH, './button/div[2]/div[1]/span[1]').text  + ' ' + product.find_element(By.XPATH , './button/div[2]/div[1]/span[2]').text

                except Exception as e:
                    format = product.find_element(By.XPATH, './button/div[2]/div[1]/span[1]').text 
                
                # PRICE
                try: 
                    price_string = product.find_element(By.XPATH, './button/div[2]/div[2]/p[1]').text.replace(',', '.')
                    price = float(price_string[:-1])
                except Exception as e:
                    logger.error("Price not found")
                    logger.exception(e)

                product_item = {
                    'name' : name,
                    'category' : category,
                    'format' : format,
                    'price' : price,
                    'timestamp' : timestamp,
                }

                print(f'{name} | CATEGORIA : {category} | PRECIO : {price} €')
                
                product_list.append(product_item)
            
            try:
                driver.execute_script('arguments[0].click()', driver.find_element(By.CLASS_NAME, 'category-detail__next-subcategory'))
                time.sleep(2)
            except NoSuchElementException:
                existSubcategory = False

    logger.info(f'Scraped {len(product_list)} products from {num_urls} urls', )
    return product_list