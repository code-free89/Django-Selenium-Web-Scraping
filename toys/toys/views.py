import pickle
from django.shortcuts import render
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from django.http import HttpResponse
import undetected_chromedriver as uc
from django.template import loader
import csv
from django.http import HttpResponse
from selenium.webdriver.common.action_chains import ActionChains
import json
from selenium.webdriver.common.keys import Keys
from django.shortcuts import render, redirect
from csv import DictWriter
import csv
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import os.path
from os import path

################################################  Scraping  section  ##################################################
# -- open browser
browser = uc.Chrome()

def scraper_init(request):
    return HttpResponse('Scraper started...')

# data scraper 
def scraper_toys(request):

    # headers in csv file
    try :
        if path.exists("toys.csv") :
            os.remove("toys.csv")
    finally :
        c= 0
    headers = ['name', 'ref', 'price', 'special price', 'home delivery in stock', 'description', 'Walsall quantity', 'Walsall in stock text', 'Wolverhampton quantity', 'Wolverhampton in stock text', 'Oldbury quantity', 'Oldbury in stock text', 'Castlevale quantity', 'Castlevale in stock text', 'image1', 'image2', 'image3', 'image4', 'image5']
    with open('toys.csv', 'a', newline='') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(headers)
        f_object.close()
    item = []
    browser.get("https://www.smythstoys.com/uk/en-gb/uk/en-gb/toys/c/SM0601")
    pickle.dump(browser.get_cookies(), open("cookies.pkl","wb"))
    print('Scraper is runing now....')
    
    # Dismiss cookie dialog

    try :
        cookie_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookieProcessed"))
        )
        ActionChains(browser).move_to_element(cookie_button).click(cookie_button).perform()
        sleep(3)
    finally :
        sleep(3)
   
    scrap_data = []
    product_links = []
    
    # Get item number

    sleep(2)
    array_string_item = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[1]/div[1]/div[2]/div/div[1]/h4").get_attribute('textContent').strip().split(' ')[0]
    number_of_items = array_string_item.replace(',', '')
    
    # Send load more button click event
    
    for i in range(int(int(number_of_items) / 60)) :
        load_more_button = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "productsLoadMore"))
        )
        ActionChains(browser).move_to_element(load_more_button).click(load_more_button).perform()
        sleep(3)
        print("click %d times" % i)
    print("Load more finished...")

    main_div = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[2]/div")

    # Get href links
    hrefs = main_div.find_elements_by_class_name("trackProduct")
    for i in range(int(len(hrefs) / 2)) :
        if i % 10 == 0:
            print("%d hrefs added" % i)
        product_links.append(hrefs[i * 2].get_attribute('href'))
    print("%d hrefs finished..." % len(product_links))
    
    # Loop product links
    
    for product_link in product_links :
        browser.get(product_link)
        sleep(4)
        name = None
        while not name:
            try:
                name = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/h1")
            except NoSuchElementException:
                time.sleep(2)
        name = name.text.strip()
        images = browser.find_elements_by_xpath("/html/body/div[7]/section/div/div/div[1]/div/div[1]/div/div[1]/div//img[@class='responsive-image']")
        image_src = ['', '', '', '', '']
        for i in range(5) :
            if i < len(images) :
                image_src[i] = images[i].get_attribute("src")
            else :
                image_src[i] = ""                
        ref_number = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/div[1]/div/div[2]/div").text.strip()[4:]
        prices = browser.find_element_by_class_name("price_tag").find_elements_by_class_name("notranslate")
        if len(prices) == 1 :
            normal_price = prices[0].text.strip()[1:]
            discount_price = ""
        else :
            normal_price = prices[1].text.strip()[1:]
            discount_price = prices[0].text.strip()[1:]
        home_delivery = browser.find_elements_by_class_name(u"homeDelivery")
        if len(home_delivery) != 0 :
            in_stock = home_delivery[0].text.strip()
        else :
            in_stock = ""
        description = ""
        description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]/div/div[1]/ul').find_elements_by_class_name("font-regular")
        if len(description_lis) :
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        else :
            description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]').findElements(By.tagName('p'))
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        # category = browser.find_elements_by_class_name(u"breadcrumb-text")[1].text
        
        # Open Store Dialog
        change_store_button = browser.find_elements_by_class_name("js-pickup-in-store-button")
        if len(change_store_button) != 0 :
            ActionChains(browser).move_to_element(change_store_button[0]).click(change_store_button[0]).perform()
            sleep(4)
            
            # Get City Stock
            try:
                WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "js-pickup-in-store-button"))
                )
            finally:
                c = 0
            Walsall_text = browser.find_elements_by_class_name("resultStock")[57].text.strip()
            if "Out of stock" in Walsall_text :
                Walsall_stock = "Out of stock"
                Walsall_quantity = ""
            else :
                Walsall_stock = "In stock"
                Walsall_quantity = Walsall_text[:-8]

            Wolverhampton_text = browser.find_elements_by_class_name("resultStock")[56].text.strip()
            if "Out of stock" in Wolverhampton_text :
                Wolverhampton_stock = "Out of stock"
                Wolverhampton_quantity = ""
            else :
                Wolverhampton_stock = "In stock"
                Wolverhampton_quantity = Walsall_text[:-8]

            Oldbury_text = browser.find_elements_by_class_name("resultStock")[59].text.strip()
            if "Out of stock" in Oldbury_text :
                Oldbury_stock = "Out of stock"
                Oldbury_quantity = ""
            else :
                Oldbury_stock = "In stock"
                Oldbury_quantity = Walsall_text[:-8]

            Castlevale_text = browser.find_elements_by_class_name("resultStock")[61].text.strip()
            if "Out of stock" in Castlevale_text :
                Castlevale_stock = "Out of stock"
                Castlevale_quantity = ""
            else :
                Castlevale_stock = "In stock"
                Castlevale_quantity = Walsall_text[:-8]
        else :
            Walsall_stock = ""
            Walsall_quantity = ""
            Wolverhampton_stock = ""
            Wolverhampton_quantity = ""
            Oldbury_stock = ""
            Oldbury_quantity = ""
            Castlevale_stock = ""
            Castlevale_quantity = ""
        
        # Save Data
        scrap_data = [
            name,
            ref_number,
            normal_price,
            discount_price,
            in_stock,
            description,
            Walsall_quantity,
            Walsall_stock,
            Wolverhampton_quantity,
            Wolverhampton_stock,
            Oldbury_quantity,
            Oldbury_stock,
            Castlevale_quantity,
            Castlevale_stock,
            image_src[0],
            image_src[1],
            image_src[2],
            image_src[3],
            image_src[4]
        ]
        save_toys(scrap_data)
    
    return HttpResponse('Scraping finished...')
def save_toys(data):
    # Create the HttpResponse object with the appropriate CSV header.
    with open('toys.csv', 'a', newline='', encoding='utf-8') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(data)
        f_object.close()
        
    return HttpResponse("Scraping toys finished...")

def scraper_baby(request):

    # headers in csv file

    try :
        if path.exists("baby.csv") :
            os.remove("baby.csv")
    finally :
        c= 0
    headers = ['name', 'ref', 'price', 'special price', 'home delivery in stock', 'description', 'Walsall quantity', 'Walsall in stock text', 'Wolverhampton quantity', 'Wolverhampton in stock text', 'Oldbury quantity', 'Oldbury in stock text', 'Castlevale quantity', 'Castlevale in stock text', 'image1', 'image2', 'image3', 'image4', 'image5']
    with open('baby.csv', 'a', newline='') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(headers)
        f_object.close()
    item = []
    browser.get("https://www.smythstoys.com/uk/en-gb/baby/c/SM0602")
    pickle.dump(browser.get_cookies(), open("cookies.pkl","wb"))
    print('Scraper is runing now....')
    
    # Dismiss cookie dialog

    sleep(10)
    try :
        cookie_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookieProcessed"))
        )
        ActionChains(browser).move_to_element(cookie_button).click(cookie_button).perform()
        sleep(3)
    finally :
        sleep(3)
   
    scrap_data = []
    product_links = []
    
    # Get item number

    sleep(2)
    array_string_item = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[1]/div[1]/div[2]/div/div[1]/h4").get_attribute('textContent').strip().split(' ')[0]
    number_of_items = array_string_item.replace(',', '')
    
    # Send load more button click event
    
    for i in range(int(int(number_of_items) / 60)) :
        load_more_button = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "productsLoadMore"))
        )
        ActionChains(browser).move_to_element(load_more_button).click(load_more_button).perform()
        sleep(3)
        print("click %d times" % i)
    print("Load more finished...")

    main_div = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[2]/div")

    # Get href links
    hrefs = main_div.find_elements_by_class_name("trackProduct")
    for i in range(int(len(hrefs) / 2)) :
        if i % 10 == 0:
            print("%d hrefs added" % i)
        product_links.append(hrefs[i * 2].get_attribute('href'))
    print("%d hrefs finished..." % len(product_links))
    
    # Loop product links
    
    for product_link in product_links :
        browser.get(product_link)
        sleep(4)
        name = None
        while not name:
            try:
                name = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/h1")
            except NoSuchElementException:
                time.sleep(2)
        name = name.text.strip()
        images = browser.find_elements_by_xpath("/html/body/div[7]/section/div/div/div[1]/div/div[1]/div/div[1]/div//img[@class='responsive-image']")
        image_src = ['', '', '', '', '']
        for i in range(5) :
            if i < len(images) :
                image_src[i] = images[i].get_attribute("src")
            else :
                image_src[i] = ""                
        ref_number = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/div[1]/div/div[2]/div").text.strip()[4:]
        prices = browser.find_element_by_class_name("price_tag").find_elements_by_class_name("notranslate")
        if len(prices) == 1 :
            normal_price = prices[0].text.strip()[1:]
            discount_price = ""
        else :
            normal_price = prices[1].text.strip()[1:]
            discount_price = prices[0].text.strip()[1:]
        home_delivery = browser.find_elements_by_class_name(u"homeDelivery")
        if len(home_delivery) != 0 :
            in_stock = home_delivery[0].text.strip()
        else :
            in_stock = ""
        description = ""
        description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]/div/div[1]/ul').find_elements_by_class_name("font-regular")
        if len(description_lis) :
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        else :
            description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]').findElements(By.tagName('p'))
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        # category = browser.find_elements_by_class_name(u"breadcrumb-text")[1].text
        
        # Open Store Dialog
        change_store_button = browser.find_elements_by_class_name("js-pickup-in-store-button")
        if len(change_store_button) != 0 :
            ActionChains(browser).move_to_element(change_store_button[0]).click(change_store_button[0]).perform()
            sleep(4)
            
            # Get City Stock
            try:
                WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "js-pickup-in-store-button"))
                )
            finally:
                c = 0
            Walsall_text = browser.find_elements_by_class_name("resultStock")[57].text.strip()
            if "Out of stock" in Walsall_text :
                Walsall_stock = "Out of stock"
                Walsall_quantity = ""
            else :
                Walsall_stock = "In stock"
                Walsall_quantity = Walsall_text[:-8]

            Wolverhampton_text = browser.find_elements_by_class_name("resultStock")[56].text.strip()
            if "Out of stock" in Wolverhampton_text :
                Wolverhampton_stock = "Out of stock"
                Wolverhampton_quantity = ""
            else :
                Wolverhampton_stock = "In stock"
                Wolverhampton_quantity = Walsall_text[:-8]

            Oldbury_text = browser.find_elements_by_class_name("resultStock")[59].text.strip()
            if "Out of stock" in Oldbury_text :
                Oldbury_stock = "Out of stock"
                Oldbury_quantity = ""
            else :
                Oldbury_stock = "In stock"
                Oldbury_quantity = Walsall_text[:-8]

            Castlevale_text = browser.find_elements_by_class_name("resultStock")[61].text.strip()
            if "Out of stock" in Castlevale_text :
                Castlevale_stock = "Out of stock"
                Castlevale_quantity = ""
            else :
                Castlevale_stock = "In stock"
                Castlevale_quantity = Walsall_text[:-8]
        else :
            Walsall_stock = ""
            Walsall_quantity = ""
            Wolverhampton_stock = ""
            Wolverhampton_quantity = ""
            Oldbury_stock = ""
            Oldbury_quantity = ""
            Castlevale_stock = ""
            Castlevale_quantity = ""
        
        # Save Data
        scrap_data = [
            name,
            ref_number,
            normal_price,
            discount_price,
            in_stock,
            description,
            Walsall_quantity,
            Walsall_stock,
            Wolverhampton_quantity,
            Wolverhampton_stock,
            Oldbury_quantity,
            Oldbury_stock,
            Castlevale_quantity,
            Castlevale_stock,
            image_src[0],
            image_src[1],
            image_src[2],
            image_src[3],
            image_src[4]
        ]
        save_baby(scrap_data)
    
    return HttpResponse('Scraping finished...')
def save_baby(data):
    # Create the HttpResponse object with the appropriate CSV header.
    with open('baby.csv', 'a', newline='', encoding='utf-8') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(data)
        f_object.close()
        
    return HttpResponse("Scraping baby rooms finished...")

def scraper_outdoor(request):

    # headers in csv file

    try :
        if path.exists("outdoor.csv") :
            os.remove("outdoor.csv")
    finally :
        c= 0
    headers = ['name', 'ref', 'price', 'special price', 'home delivery in stock', 'description', 'Walsall quantity', 'Walsall in stock text', 'Wolverhampton quantity', 'Wolverhampton in stock text', 'Oldbury quantity', 'Oldbury in stock text', 'Castlevale quantity', 'Castlevale in stock text', 'image1', 'image2', 'image3', 'image4', 'image5']
    with open('outdoor.csv', 'a', newline='') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(headers)
        f_object.close()
    item = []
    browser.get("https://www.smythstoys.com/uk/en-gb/outdoor/c/SM0603")
    pickle.dump(browser.get_cookies(), open("cookies.pkl","wb"))
    print('Scraper is runing now....')
    
    # Dismiss cookie dialog

    sleep(10)
    try :
        cookie_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookieProcessed"))
        )
        ActionChains(browser).move_to_element(cookie_button).click(cookie_button).perform()
        sleep(3)
    finally :
        sleep(3)
   
    scrap_data = []
    product_links = []
    
    # Get item number

    sleep(2)
    array_string_item = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[1]/div[1]/div[2]/div/div[1]/h4").get_attribute('textContent').strip().split(' ')[0]
    number_of_items = array_string_item.replace(',', '')
    
    # Send load more button click event
    
    for i in range(int(int(number_of_items) / 60)) :
        load_more_button = WebDriverWait(browser, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "productsLoadMore"))
        )
        ActionChains(browser).move_to_element(load_more_button).click(load_more_button).perform()
        sleep(3)
        print("click %d times" % i)
    print("Load more finished...")

    main_div = browser.find_element_by_xpath("/html/body/div[7]/div[1]/div[2]/div[3]/div/div[1]/div[2]/div")

    # Get href links
    hrefs = main_div.find_elements_by_class_name("trackProduct")
    for i in range(int(len(hrefs) / 2)) :
        if i % 10 == 0:
            print("%d hrefs added" % i)
        product_links.append(hrefs[i * 2].get_attribute('href'))
    print("%d hrefs finished..." % len(product_links))
    
    # Loop product links
    
    for product_link in product_links :
        browser.get(product_link)
        sleep(4)
        name = None
        while not name:
            try:
                name = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/h1")
            except NoSuchElementException:
                time.sleep(2)
        name = name.text.strip()
        images = browser.find_elements_by_xpath("/html/body/div[7]/section/div/div/div[1]/div/div[1]/div/div[1]/div//img[@class='responsive-image']")
        image_src = ['', '', '', '', '']
        for i in range(5) :
            if i < len(images) :
                image_src[i] = images[i].get_attribute("src")
            else :
                image_src[i] = ""                
        ref_number = browser.find_element_by_xpath("/html/body/div[7]/section/div/div/div[2]/div[1]/div[1]/div/div[2]/div").text.strip()[4:]
        prices = browser.find_element_by_class_name("price_tag").find_elements_by_class_name("notranslate")
        if len(prices) == 1 :
            normal_price = prices[0].text.strip()[1:]
            discount_price = ""
        else :
            normal_price = prices[1].text.strip()[1:]
            discount_price = prices[0].text.strip()[1:]
        home_delivery = browser.find_elements_by_class_name(u"homeDelivery")
        if len(home_delivery) != 0 :
            in_stock = home_delivery[0].text.strip()
        else :
            in_stock = ""
        description = ""
        description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]/div/div[1]/ul').find_elements_by_class_name("font-regular")
        if len(description_lis) :
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        else :
            description_lis = browser.find_element_by_xpath(u'//*[@id="profile"]').findElements(By.tagName('p'))
            for description_li in description_lis :
                description = description + description_li.text.strip() + "<br/>"
        # category = browser.find_elements_by_class_name(u"breadcrumb-text")[1].text
        
        # Open Store Dialog
        change_store_button = browser.find_elements_by_class_name("js-pickup-in-store-button")
        if len(change_store_button) != 0 :
            ActionChains(browser).move_to_element(change_store_button[0]).click(change_store_button[0]).perform()
            sleep(4)
            
            # Get City Stock
            try:
                WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "js-pickup-in-store-button"))
                )
            finally:
                c = 0
            Walsall_text = browser.find_elements_by_class_name("resultStock")[57].text.strip()
            if "Out of stock" in Walsall_text :
                Walsall_stock = "Out of stock"
                Walsall_quantity = ""
            else :
                Walsall_stock = "In stock"
                Walsall_quantity = Walsall_text[:-8]

            Wolverhampton_text = browser.find_elements_by_class_name("resultStock")[56].text.strip()
            if "Out of stock" in Wolverhampton_text :
                Wolverhampton_stock = "Out of stock"
                Wolverhampton_quantity = ""
            else :
                Wolverhampton_stock = "In stock"
                Wolverhampton_quantity = Walsall_text[:-8]

            Oldbury_text = browser.find_elements_by_class_name("resultStock")[59].text.strip()
            if "Out of stock" in Oldbury_text :
                Oldbury_stock = "Out of stock"
                Oldbury_quantity = ""
            else :
                Oldbury_stock = "In stock"
                Oldbury_quantity = Walsall_text[:-8]

            Castlevale_text = browser.find_elements_by_class_name("resultStock")[61].text.strip()
            if "Out of stock" in Castlevale_text :
                Castlevale_stock = "Out of stock"
                Castlevale_quantity = ""
            else :
                Castlevale_stock = "In stock"
                Castlevale_quantity = Walsall_text[:-8]
        else :
            Walsall_stock = ""
            Walsall_quantity = ""
            Wolverhampton_stock = ""
            Wolverhampton_quantity = ""
            Oldbury_stock = ""
            Oldbury_quantity = ""
            Castlevale_stock = ""
            Castlevale_quantity = ""
        
        # Save Data
        scrap_data = [
            name,
            ref_number,
            normal_price,
            discount_price,
            in_stock,
            description,
            Walsall_quantity,
            Walsall_stock,
            Wolverhampton_quantity,
            Wolverhampton_stock,
            Oldbury_quantity,
            Oldbury_stock,
            Castlevale_quantity,
            Castlevale_stock,
            image_src[0],
            image_src[1],
            image_src[2],
            image_src[3],
            image_src[4]
        ]
        save_outdoor(scrap_data)
    
    return HttpResponse('Scraping finished...')
def save_outdoor(data):
    # Create the HttpResponse object with the appropriate CSV header.
    with open('outdoor.csv', 'a', newline='', encoding='utf-8') as f_object:
        writer_object = csv.writer(f_object)
        writer_object.writerow(data)
        f_object.close()
        
    return HttpResponse("Scraping outdoor finished...")
