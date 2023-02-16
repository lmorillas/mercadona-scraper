#!/usr/bin/python3

import logging
from os.path import devnull


import time 
import datetime

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By 

logger = logging.getLogger()



def get_category_products(driver, category_urls):

    product_list = []
    scraped = ''
    # TIMESTAMP
    unixtime = time.time()
    timestamp = datetime.datetime.fromtimestamp(unixtime).date()
    num_urls = 1

    # TODO : arreflar guantes
    guante_counter = 0

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

                # TODO : find better solution for this
                # BOSQUE-VERDE condition

                guantes = ['guantes de látex bosque verde talla pequeña', 'guantes de látex bosque verde talla mediana', 'guantes de látex bosque verde talla grande']
                
                if name.lower() in guantes:
                    if guante_counter > 2:

                        name += ' (revestidos)'

                    else: 
                        name += ' (sensibles)'
                        guante_counter += 1

                product_item = {
                    'name' : name,
                    'category' : category,
                    'format' : format,
                    'price' : price,
                    'timestamp' : timestamp,
                }

                scraped += f'{name} | CATEGORIA : {category} | PRECIO : {price} €\n'
                
                product_list.append(product_item)
                              
            
            try:
                driver.execute_script('arguments[0].click()', driver.find_element(By.CLASS_NAME, 'category-detail__next-subcategory'))
                time.sleep(2)
            except NoSuchElementException:
                existSubcategory = False

    with open(f'scraped/{timestamp}.txt', 'w') as f:
        f.write(scraped)

    logger.info(f'Scraped {len(product_list)} products from {num_urls} urls')
    return product_list