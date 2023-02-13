#!/usr/bin/python3

import logging

 
from selenium.webdriver.common.by import By 


logger = logging.getLogger()

def get_urls(driver):


    category_urls = []
    category_list = driver.find_elements(By.CLASS_NAME, 'category-menu__item')
    
    for item in category_list:

        button = item.find_element(By.XPATH, './div/button')

        driver.execute_script('arguments[0].click()', button)

        url = driver.current_url

        category_urls.append(url)
        driver.back()

    return category_urls