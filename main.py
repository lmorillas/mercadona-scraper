import logging


import sqlite3
import pandas as pd
 
from urls import get_urls
from products import get_category_products

logging.basicConfig(filename='logs/app.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger()

HOME_URL =  "https://tienda.mercadona.es/categories/"



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

    # fetch urls
    category_urls = get_urls()

    # LOG DATA FOR URLS
    
    # fetch product data
    product_data = get_category_products(category_urls)

    # save data to csv
    save_data(product_data)