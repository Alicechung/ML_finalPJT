### Project Alda
### Enrollment Crawler
### Ningyin Xu Mar. 4th

###############################################################################
    
    # To run this, you need to install selenium package, and its phantom driver.
    # Reference Webpage:
    # http://stackoverflow.com/questions/13287490/is-there-a-way-to-use-phantomjs-in-python

###############################################################################


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
import smtplib
import getpass
from datetime import datetime
from threading import Timer


COURSE_URL = 'https://coursesearch.uchicago.edu/psc/prdguest/EMPLOYEE/HRMS/c/UC_STUDENT_RECORDS_FL.UC_CLASS_SEARCH_FL.GBL'


def setup_driver(course_url):
    '''
    Setup PhantomJS, redirect to Course Search page, fix quarter as "Spring 2017".
    Get ready to scrape in this page.
    '''
    dothething = True
    while dothething:
        try:
            driver = webdriver.PhantomJS()
            driver.implicitly_wait(10)
            driver.set_window_size(1024,768)
            driver.get(course_url)
            quarter_select = Select(driver.find_element_by_id('UC_CLSRCH_WRK2_STRM'))
            if quarter_select.first_selected_option.text != 'Spring 2017':
                quarter_select.select_by_value('2174')
            driver.save_screenshot('screen.png')
            driver.implicitly_wait(20)
            print('driver ready')
            return driver
            break
        except StaleElementReferenceException:
            driver.quit()
            continue
        except NoSuchElementException:
            driver.quit()
            continue


def course_enroll(course_dept, course_num):
    '''
    Given course name, scrape the enrollment info.
    '''
    driver = setup_driver(COURSE_URL)

    course_search = course_dept + ' ' + course_num
    searchcontent = driver.find_element_by_id('UC_CLSRCH_WRK2_PTUN_KEYWORD')
    searchcontent.send_keys(course_search)
    searchbtn = driver.find_element_by_id('UC_CLSRCH_WRK_SSR_PB_SEARCH')
    searchbtn.click()

    wait = WebDriverWait(driver, 20)
    wait.until(EC.staleness_of(searchbtn))
    driver.save_screenshot('screen_enroll.png')

    try:
        enrollinfo = driver.find_element_by_id('UC_CLSRCH_WRK_DESCR1$0').text
        enrollnum = enrollinfo.split()[-1]
        enrollnum = enrollnum.split('/')
        curenroll = int(enrollnum[0])
        totalenroll = int(enrollnum[1])

        if curenroll < totalenroll:
            driver.quit()
            return True
        else:
            print('current enroll exceeds total enrollment')
            return False
    except NoSuchElementException:
        print('Enrollment information somehow unavailable')
        driver.quit()
        return False


def main(course_dept, course_num, emailto):
    '''
    main function, sending email notification.
    '''
    enroll = course_enroll(course_dept, course_num)

    if enroll:
        username = 'janicexu423@gmail.com'
        FROM = username
        TO = [emailto]
        TEXT = "Course: " + course_dept + course_num + ' is currently available.'
        SUBJECT = "Enrollment Information"
        message = """\                                       
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        password = 'Jessie423324'
        server.login(username, password)
        server.sendmail(FROM, TO, message)
        server.quit()
        return True
    else:
        return False























    
