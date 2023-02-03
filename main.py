import logging


import time 
import datetime
import sqlite3
import pandas as pd
 
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver 
from selenium.webdriver import Firefox 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.firefox import GeckoDriverManager


logging.basicConfig(filename='logs/app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()

HOME_URL =  "https://tienda.mercadona.es/categories/"

def get_urls():
    
    driver.get(HOME_URL)

    category_urls = []
    category_list = driver.find_elements(By.CLASS_NAME, 'category-menu__item')
    
    for item in category_list:

        button = item.find_element(By.XPATH, './div/button')

        driver.execute_script('arguments[0].click()', button)

        url = driver.current_url

        category_urls.append(url)
        driver.back()

    return category_urls

def get_category_products(category_urls):

    driver.get(HOME_URL)
    
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


def save_data(product_data):

    connection = sqlite3.connect('data.db')
    
    try: 
        df = pd.DataFrame(product_data)
        df.to_sql('productdata', connection, if_exists='append', index=False,)
        logger.debug('Connection to database Successful')

    except Exception as e:
        logger.exception('Problem while saving data to database')

def scrape_data():
    category_urls = get_urls()
    product_data = get_category_products(category_urls)
    save_data(product_data)


if __name__ == '__main__':


    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


    options = webdriver.FirefoxOptions()
    options.headless = True # 


    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
    options.page_load_strategy = 'none'

    # path web driver downloaded
    firefox_path = GeckoDriverManager().install()
    firefox_service = Service(firefox_path)

    # defined options
    driver = Firefox(options=options, service=firefox_service)
    driver.implicitly_wait(3)

    # get url and wait
    driver.get(HOME_URL)
    
    # Request data
    try:
        cookie_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div/div/button[2]')
        driver.execute_script('arguments[0].click()', cookie_button)
    
    except Exception as e:
        logger.exception('Problem while accepting cookies', exc_info=True)

    try: 
        form = driver.find_element(By.CLASS_NAME, 'postal-code-checker')
        input = form.find_element(By.XPATH, './div/input')
        input.send_keys('28039')
        submit_button = form.find_element(By.XPATH, './button')
        driver.execute_script('arguments[0].click()', submit_button)

    except Exception as e:
        logger.exception('No se ha podido introducir CP', exc_info=True)


    # fetch urls
    category_urls = get_urls()

    # LOG DATA FOR URLS
    
    # fetch product data
    product_data = get_category_products(category_urls)

    # save data to csv
    save_data(product_data)