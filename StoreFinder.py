from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import json


with open('config.json') as json_file:
    config = json.load(json_file)

print("Configure:\n[0] Driver\n[1] Driver path\n[2] Product site\n[3] Zip code\n[4] Max stores")
configure_options = input("Type i.e. 1,2,4 to configure these options or press ENTER to load existing configuration:")

for config_option in configure_options.split(','):
    if config_option == '0':
        config['driver'] = input("[0] Select your driver [chrome, edge, firefox, safari]: ")
    elif config_option == '1':
        config['driver_path'] = input("[1] Enter your driver path (i.e. ~/chromedriver): ")
    elif config_option == '2':
        config['product_site'] = input("[2] Enter the Rewe product site: ")
    elif config_option == '3':
        config['zip'] = input("[3] Enter your zip code: ")
    elif config_option == '4':
        config['max_stores'] = input("[4] Enter how many stores should be searched. Press ENTER to select maximum available: ")

with open('config.json', 'w') as outfile:
    json.dump(config, outfile, indent=3)

print("Loaded configuraton: ", config)

# user defined
# driver_path = "/mnt/data/Projects/Programming/ReweStoreFinder/chromedriver"
# product_site = 'https://shop.rewe.de/p/breyers-delights-peanut-butter-vegan-500ml/8295089'
# zipcode = "10625"
# max_stores_input = 3

driver_path = config['driver_path']
product_site = config['product_site']
zipcode = config['zip']
if config['max_stores'] == "":
    max_stores_input = None
else:
    max_stores_input = int(config['max_stores'])

# Driver selection
if config['driver'] == 'chrome':
    browser = webdriver.Chrome(driver_path)
elif config['driver'] == 'firefox':
    browser = webdriver.Firefox(driver_path)
elif config['driver'] == 'safari':
    browser = webdriver.Safari(driver_path)
elif config['driver'] == 'edge':
    browser = webdriver.Edge(driver_path)



# rewe product site selection
browser.get(product_site)

def wait_find_element(by, class_name):
    return WebDriverWait(browser, 3).until(
        EC.presence_of_element_located((
            by, class_name)))


def is_product_available():
    try:
        browser.find_element_by_class_name("pdr-NotAvailable__text--strong")
    except NoSuchElementException:
        return False
    else:
        return True

# search other location
stores_information = []

i = 0
max_stores = 2 # arbitary number to iterate through the loop at least once
while i < max_stores:
    if i == 0:
        # first time selecting store. Sometimes the "Standort waehlen" ist mixed up
        try:
            wait_find_element(By.CLASS_NAME, "pdr-ChangeServiceButton").click()
        except TimeoutException:
            wait_find_element(By.CLASS_NAME, "gbmc-header-button__mc-trigger").click()

        zip_code = wait_find_element(By.ID, "marketchooser-search-value")
        zip_code.send_keys(zipcode)
        zip_code.send_keys(Keys.ENTER)

    else:
        # goto find other stores
        browser.get(product_site) # refresh because the dom need to re read
        wait_find_element(By.CLASS_NAME, "gbmc-header-button__mc-trigger").click()

    # pickup selection
    wait_find_element(By.CLASS_NAME, "pickup-service-description").click()

    # stores
    stores_html = wait_find_element(By.ID, "list-item").find_elements_by_xpath("./*")
    if max_stores_input == None:
        max_stores = len(stores_html)
    else:
        if max_stores_input > len(stores_html):
            max_stores = len(stores_html)
        else:
            max_stores = max_stores_input

    # save name and distance
    store = stores_html[i]
    adress = store.find_element_by_class_name("market-item__address").text
    distance = store.find_element_by_class_name("market-item__distance").text

    # save store information
    store_info = {}
    store_info['adress'] = adress
    store_info['distance'] = distance
    stores_information.append(store_info)

    # select specific store
    store.find_element_by_tag_name("button").click()


    # goto shop
    wait_find_element(By.CLASS_NAME, "mc-primary-button__label").click()
    stores_information[i]['available'] = is_product_available()

    print("Searching in ", store_info)

    i += 1

print(stores_information)