##############################################
## Script to extract project data from
## fDi Markets
##############################################
# Modules:
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from lxml import html
from bs4 import BeautifulSoup, SoupStrainer
import re
import time
import os
import csv
import sys
import numpy
import string
import random
##############################################
# Working directory:
# os.chdir("/Users/robertgulotty/Dropbox/FDI_Data/Data/")
os.chdir("/Users/robertgulotty/Dropbox/FDI_Data/Data/")
login_url = "http://app.fdimarkets.com/library/go"
driver = webdriver.Chrome()
driver.get(login_url)
# Enter login information manually and accept terms.
##############################################
# Load Project Database:
proj_url = "http://app.fdimarkets.com/library/index.cfm?ck=73721194&fuseaction=project_database.default&undefined"
driver.get(proj_url)

# Expanding to 20 records:
elem = driver.find_element_by_css_selector("a[title='20 Records per page']")
elem.click()

time.sleep(10)
 
# Expanding project text:
elem = driver.find_element_by_css_selector("a[title='View each project in the table in greater detail (detailed mode)']")
elem.click()
# Total number of pages:
total_pages = 9434
page_vec = range(1, total_pages)
##############################################
# Set pages to loop over:
# This needs to be changed for each session.
begin_page = 9348
end_page = begin_page + 250
base = 'fDiMarkets_project_html_'
file_name =  base + str(begin_page) + '_' + str(end_page) + '.txt'
print file_name
##############################################

delay = 30

# This loops over project searches and copy/pastes the html:
with open(file_name, 'wb') as txt_file:
	for num in page_vec[begin_page:end_page]:
		# Getting page of results:
		page_field = driver.find_element_by_id("page_index")
		page_field.clear()
		page_field.send_keys(str(num))
		driver.find_element_by_css_selector("img[title=\"Skip to page\"]").click()
		##############################################
		# This will wait up to 20 secs for the page to load:
		expr = "Page " + str(num) + " of 9,434"
		locator = "//*[contains(text(), " + "'" + expr + "'" + ")]"
		try:
		    # WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[title=\"Skip to page\"]")))
		    WebDriverWait(driver, delay).until(
		    	EC.presence_of_element_located((By.XPATH, locator)))
		except TimeoutException:
		    print "Loading exceeds delay."
		##############################################
		# Extracting unparsed html:
		html = driver.page_source
		soup = BeautifulSoup(html)
		out = []
		for t in soup.find_all('tr', id = re.compile('row_')):
			out.append(t.contents)
		for item in out:
  			txt_file.write("%s\n" % item)
  		##############################################
  		time.sleep(1 + random.random() * 3)
  		print "Completed " + str(page_vec[num])
txt_file.close()

print num
