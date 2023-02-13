#!/usr/bin/python3

import logging
import os

import sqlite3
import pandas as pd
import datetime
import time 


from selenium import webdriver 
from selenium.webdriver import Firefox 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service 
from webdriver_manager.firefox import GeckoDriverManager

from urls import get_urls
from products import get_category_products


unixtime = time.time()
timestamp = datetime.datetime.fromtimestamp(unixtime).date().strftime('%d-%m-%Y')
 

logging.basicConfig(filename=f'logs/{timestamp}.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()

HOME_URL =  "https://tienda.mercadona.es/categories/"


def save_data(product_data):

    current = os.getcwd()
    db_dir = os.path.join(current, 'data.db')
    connection = sqlite3.connect(db_dir)
    
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

    
    HOME_URL =  "https://tienda.mercadona.es/categories/"


    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--headless')
    firefox_options.set_preference("browser.cache.disk.enable", False)
    firefox_options.set_preference("browser.cache.memory.enable", False)
    firefox_options.set_preference("browser.cache.offline.enable", False)
    firefox_options.set_preference("network.http.use-cache", False)
    firefox_options.set_preference("browser.privatebrowsing.autostart", True)


    # firefox service
    firefox_path = GeckoDriverManager().install()
    firefox_service = Service(firefox_path, log_path=os.path.devnull)

    # defined options
    driver = Firefox(options=firefox_options, service=firefox_service)
    driver.implicitly_wait(3)

    # get url and wait
    driver.get(HOME_URL)


    # fetch urls
    category_urls = get_urls(driver)

    # LOG DATA FOR URLS
    
    # fetch product data
    product_data = get_category_products(driver, category_urls)

    # save data to csv
    save_data(product_data)

    driver.close()
    driver.quit()


