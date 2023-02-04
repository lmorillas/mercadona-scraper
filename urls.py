import logging


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


def get_urls():
    

    category_urls = []
    category_list = driver.find_elements(By.CLASS_NAME, 'category-menu__item')
    
    for item in category_list:

        button = item.find_element(By.XPATH, './div/button')

        driver.execute_script('arguments[0].click()', button)

        url = driver.current_url

        category_urls.append(url)
        driver.back()

    return category_urls