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
from selenium.webdriver.support.ui import Select
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
os.chdir("C:/Users/minju/Dropbox/UChicago/MA Thesis/TAA/datascraping")
driver = webdriver.Chrome()
driver.get("https://www.doleta.gov/tradeact/taa_reports/petitions.cfm")

#State_list
state_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT',
'DE', 'DC', 'FL', 'GA', 'HI','ID', 'IL', 'IN', 'IA',
'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
'ND', 'OH', 'OK', 'OR','PA', 'PR', 'RI', 'SC', 'SD',
'TN', 'TX', 'UT', 'VT','VA', 'WA', 'WV', 'WI', 'WY']

#Create html
taafun = "taafun.txt"
print taafun

delay=30

# This loops over project searches and copy/pastes the html:
with open(taafun, 'wb') as txt_file:
    
   i = 0
   for j in range(2001, 2017+1):
       for state in state_list:
          stateselector = Select(driver.find_element_by_name("state"))
          stateselector.select_by_value(str(state))

          driver.find_element_by_id("fromdt").clear()
          frombox = driver.find_element_by_name("fromdt")
          frombox.send_keys("01/01/{}".format(j))
          driver.find_element_by_id("todt").clear()
          tobox = driver.find_element_by_name("todt")
          tobox.send_keys("12/31/{}".format(j))

          if i==0:
              element1 = driver.find_element_by_xpath("//input[@id='filed']")
              element1.click()
              element2 = driver.find_element_by_xpath("//input[@id='certified']")
              element2.click()
              element3 = driver.find_element_by_xpath("//input[@id='denied']")
              element3.click()
          i= i + 1
          
          submit = driver.find_element_by_xpath("//input[@id='submit']")
          submit.click()

          
          #Extracting unparsed html
          html = driver.page_source
          soup = BeautifulSoup(html, "html.parser")
          out = []

          for x in soup.find_all("td", {"align" : "right"}):
              out.append([x.contents,j,state])
          for item in out:
              txt_file.write("%s\n" % item)
          print state

          time.sleep(3)


          back = driver.find_element_by_xpath("//*[text()='Back']")
          back.click()
                    
txt_file.close()
print state



      
