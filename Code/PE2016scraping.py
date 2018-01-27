from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
#from lxml import html
#from bs4 import BeautifulSoup, SoupStrainer
from selenium.webdriver.support.ui import Select
import re
import time
import os
import csv
import sys
#import numpy
import string
import random


"""Get the browser (a "driver")."""

# find the path with 'which chromedriver'
path_to_chromedriver = ('/Users/misun/Desktop/chromedriver')
browser = webdriver.Chrome(executable_path=path_to_chromedriver)

url = "http://www.presidency.ucsb.edu/index_docs.php"
browser.get(url)
time.sleep(5)

# 2008 Presidential Election
pe_2008 = browser.find_element_by_xpath(
    "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/ul/li[22]/ul/li[5]/a")

# 2012 Presidential Election
pe_2012 = browser.find_element_by_xpath(
    "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/ul/li[22]/ul/li[6]/a")

# 2016 Presidential Election
pe_2016 = browser.find_element_by_xpath(
    "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/table/tbody/tr/td/table/tbody/tr/td/ul/li[22]/ul/li[7]/a")

pe_2016.click()

pathls=['3','7','9', '11', '13', '17', '21', '23', '25', '27', '29', '31', '33', '35', '37', '39',
       '41', '43', '45', '47', '49']
for i in pathls :
    path = '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/p[1]/table/tbody/tr/td/table/tbody/tr['+i+']/td[2]/p[2]/a[1]'
    cand_ele = browser.find_element_by_xpath(path)
    cand_ele.click()
    
    #Create text file
    candidatename = browser.find_element_by_xpath('//td[@class = "listdate"]').text
    campaign = "campaign" + candidatename +'.txt'


    # This loops over project searches and copy/pastes the html:
    with open(campaign, 'w') as txt_file:

        row_num = len(browser.find_elements_by_xpath("/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr"))

        for i in range(2, row_num + 1):
            path_one = "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr["
            path_two = "]/td[3]/a"
            ele = browser.find_element_by_xpath(path_one+str(i)+path_two)
            ele.click()

            # title , docdate and textbody
            title = browser.find_element_by_xpath('.//span[@class = "paperstitle"]').text
            docdate = browser.find_element_by_xpath('.//span[@class = "docdate"]').text
            textbody = browser.find_element_by_xpath('.//span[@class = "displaytext"]').text
            
            txt_file.write("%s\n" % title)
            txt_file.write("\n")
            txt_file.write("%s\n" % docdate)
            txt_file.write("\n")            
            txt_file.write("%s\n" % textbody)
            txt_file.write("\n\n")

            time.sleep(3)

            browser.back()
        
        txt_file.close()
        print(candidatename, ' done.')
        
    browser.back()
print('Finally Finished. 2016')   