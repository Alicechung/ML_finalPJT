#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 22:22:34 2017

@author: luxihan
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import bs4
import getpass
import json
import time
import signal
import csv
import re
import pickle
import sqlite3


quarter_dict = {'autumn': 1, 'winter': 2, 'spring': 3, 'summer':4}
#### Time Out Handler#####
def signal_handler(signum, frame):
    '''
    A timer to stop a job
    '''
    raise Exception("Timeout!")

signal.signal(signal.SIGALRM, signal_handler)


############################

###Scraping Functions#########
def log_in(driver, eval_url):
    '''
    Given a driver and a url, try to login to the evluation site
    and return the cookie, user name and password
    '''
    driver.implicitly_wait(10)
    username_field = driver.find_element_by_id('username')
    password_field = driver.find_element_by_id('password')
    user_name = input('Username: ')
    password = getpass.getpass("Password: ")
    print('Username: {} password received!'.format(user_name))
    username_field.send_keys(user_name)
    password_field.send_keys(password)
    submit_field = driver.find_element_by_xpath("//button[@type = 'submit']")
    submit_field.click()
    cookie_dict = driver.get_cookies()
    while len(cookie_dict) > 2:
        cookie_dict = driver.get_cookies()
    cookie = {i['name'] : i['value'] for i in cookie_dict}
    return cookie, user_name, password

def relog_in(driver, eval_url, user_name, password):
    '''
    Given the driver, url, user name and the password
    try to relog into  the site. Built for cookie expiring
    '''
    driver.implicitly_wait(10)
    username_field = driver.find_element_by_id('username')
    password_field = driver.find_element_by_id('password')
    username_field.send_keys(user_name)
    password_field.send_keys(password)
    submit_field = driver.find_element_by_xpath("//button[@type = 'submit']")
    submit_field.click()
    cookie_dict = driver.get_cookies()
    while len(cookie_dict) > 2:
        cookie_dict = driver.get_cookies()
    cookie = {i['name'] : i['value'] for i in cookie_dict}
    return cookie


def get_request(eval_url, cookie, search_terms = None):
    '''
    Given url, cookie and the search term, try to retrieve the
    request object and web page
    '''
    session = requests.Session()
    # if we don't have a search term
    if search_terms != None:
        while True:
            signal.alarm(5)
            try:    
                req = session.get(eval_url + 'index.php', params = search_terms,\
                                 cookies = cookie.copy())
                
            except: ## if the request takes more than 5 seconds to request
                print('Connection Error.... Retry')
                signal.alarm(0)
                time.sleep(0.5)
                continue
            else:
                signal.alarm(0)
                break
    else:
        counter = 1
        while True:
            # if the webpage takes more than 20 times to request
            if counter > 20:
                return None, None
            signal.alarm(15)
            try:
                signal.alarm(15)
                req = session.get(eval_url, cookies = cookie.copy())
            except:
                print('Connection Error.... Retry')
                print(eval_url)
                signal.alarm(0)
                time.sleep(0.5)
                counter += 1
                continue
            else:
                signal.alarm(0)
                break
        
    page = bs4.BeautifulSoup(req.content, "lxml")
    return req, page


def find_dept_year_list(eval_url, cookie):
    '''
    Given the url and the cookie, try to get all of the department
    year in the evluatoin site
    '''
    req, page = get_request(eval_url, cookie)
    dept_list = page.find_all('select', attrs = {'id' : 'department', 'name' : 'Department'})
    dept = dept_list[0]
    opt = dept.find_all('option')
    dept_list = []
    for i in opt:
        # the first term in the drop down menu is 'department'
        if i.text == 'Department':
            continue
        else:
            dept_list.append(i['value'])

    year_list = page.find_all('select', attrs = {'id' : 'AcademicYear', 'name' : 'AcademicYear'})
    year = year_list[0]
    opt = year.find_all('option')
    year_list = []
    for i in opt:
        if i.text == 'Academic Year':
            continue
        else:
            year_list.append(i['value'])
    return dept_list, year_list


def compile_course_num(eval_url, cookie, dept_list, year_list):
    '''
    Given the url, the cookie, a list of department and a list of
    year to scrape, return a dictionary that document the unique 
    identifier of the courses
    '''
    course_num_set = set()
    course_num_dict = {}    
    for i, dept in enumerate(dept_list):
        for year in year_list:
            search_terms = {'Department': dept, 'AcademicYear': year,\
                            'EvalSearchType':'option-dept-search'}
            cur_req, cur_page = get_request(eval_url, cookie, search_terms)
            table = cur_page.find('tbody')
            if table == None:
                continue
            rows = table.find_all('tr')
            for row in rows:
                course_num = row.find_all('td')[0].text
                course_num = ' '.join(course_num.split()[0:2])
                course_num_set.add(course_num)
        print("At the {}th department {}, year{}".format(i, dept, year))
    course_num_list = sorted(list(course_num_set))
    # give the unique identifiers
    count = 0
    for course in course_num_list:
        count += 1
        course_num_dict[course] = count
    return course_num_dict


def compile_instructor_num(eval_url, cookie, dept_list, year_list, count):
    '''
    Given the url, the cookie, a list of department and a list of
    year  and a starting identifier
    to scrape, return a dictionary that document the unique 
    identifier of the courses and the ending identifier for the last
    instructor
    '''
    instructor_num_set = set()
    instructor_num_dict = {}
    for i, dept in enumerate(dept_list):
        for year in year_list:
            print("At the {}th department {}, year{}".format(i, dept, year))
            search_terms = {'Department': dept, 'AcademicYear': year,\
                            'EvalSearchType':'option-dept-search'}
            cur_req, cur_page = get_request(eval_url, cookie, search_terms)
            table = cur_page.find('tbody')
            if table == None:
                continue
            rows = table.find_all('tr')
            for row in rows:
#                time.sleep(0.3)
#                start = time.time()
                new_url = eval_url + row.find('a')['href']
                new_req, new_page = get_request(new_url, cookie)
                if new_req == None:
                    continue
#                print("load the page", time.time() - start)
                page_paragraph = new_page.find('p')
                if page_paragraph != None:
                    if len(page_paragraph.contents)>1:
                        instructors = str(new_page.find('p').contents[2])
                        instructor_list = instructors.split(';')
                    # avoid evluation not found
                    else:
                        instructors = row.find_all('td')[2].text
                        instructor_list = instructors.split(';')
                ## if the evluation page is blank
                else:
                    instructors = row.find_all('td')[2].text
                    instructor_list = instructors.split(';')
                ## If the evaluation page is blank in the instrucotr section
                if len(instructor_list) == 1 and instructor_list[0].strip() == '':
                    instructors = row.find_all('td')[2].text
                    instructor_list = instructors.split(';')
                    print('Blank instructor: Instructor {} Department {} Year {}'\
                          .format(instructors, dept, year))
                    ## if all of the instructor slots are blank then fill in
                    ## Unknown Instructor
                    if len(instructors.strip()) == 0:
                        instructors = "Unknown Instructor"
                        instructor_list = instructors.split(';')
                for instructor in instructor_list:
                    if ',' in instructor:
                        name_list = instructor.split(',')
                        name_list = [i.strip().lower() for i in name_list]
                    else:
                        name_list = instructor.split()
                        name_list = [i.lower() for i in name_list]
                        name_list = [name_list[0], ' '.join(name_list[1:])]
#                    name_tup = tuple([i.strip().lower() for i in name_list])
                    name = ', '.join(name_list)
                    name_tup = (name, dept)
                    instructor_num_set.add(name_tup)
#                print("find instructor", time.time() - start)
        print("At the {}th department {}, year{}".format(i, dept, year))
    instructor_num_list = sorted(list(instructor_num_set))
    for instruct_tup in instructor_num_list:
        count += 1
        name, dept = instruct_tup
        instructor_list = instructor_num_dict.get(name, [])
        instructor_list.append((count, dept))
        instructor_num_dict[name] = instructor_list
    return instructor_num_dict, count




def create_main_table(eval_url, cookie, dept_list, year_list, course_num_dict,\
                      instructor_num_dict, overwrite = True):
    '''
    A function to construct the csv for the instructors and courses.
    '''
    course_table_dict = {} 
    instructor_table_dict = {}
    link_table_list = []
    url_list = []
    err_count = 0
    for i, dept in enumerate(dept_list):
        for year in year_list:
            print(dept, year)
            search_terms = {'Department': dept, 'AcademicYear': year,\
                            'EvalSearchType':'option-dept-search'}
            cur_req, cur_page = get_request(eval_url, cookie, search_terms)
            table = cur_page.find('tbody')
            if table == None:
                continue
            rows = table.find_all('tr')
            for row in rows: 
                id_tracker = set()
                link_table_class_list = []
                course_list = row.find_all('td')
                ## construct course table
                course_num = course_list[0].text
                course_title = course_list[1].text.strip()
                course_num = ' '.join(course_num.split()[0:2])
                class_section = course_list[0].text.split()[-1].strip()
                quarter = quarter_dict[course_list[-1].text.split()[0].strip().lower()]
                course_id = course_num_dict[course_num]
                if course_num not in course_table_dict:
                    course_table_dict[course_num] = [course_num, course_id, \
                                     course_title, dept]
                
                ## construct instructor table
                instructor_list = course_list[2].text.split(';')
                for name in instructor_list:
#                    name is blank
                    name = name.replace(',', ' ')
                    name_list = name.strip().lower().split()
                    # if no name is found the nreturn nothing
                    if name_list == []:
                        continue
                    last_name = name_list[0]
                    first_name = ' '.join(name_list[1:])
                    full_name = ', '.join([last_name, first_name])
                    # if the name of the instructor is in the identifer dict
                    if full_name in instructor_num_dict:
                        for tup in instructor_num_dict[full_name]:
                            # if the instructor is in the same department as
                            # indicated in the instructor dict
                            if dept == tup[1]:
                                instructor_id = tup[0]
                        link_table_class_list.append([instructor_id])
                        if full_name not in instructor_table_dict:
                            instructor_table_dict[full_name] = [last_name, \
                                                 first_name, instructor_id,dept]
                    # if not in the instructor dict
                    else:
                        # case I; name order is wrong
                        last_name = name_list[-1]
                        first_name = ' '.join(name_list[:-1])
                        full_name = ', '.join([last_name, first_name])
                        if full_name in instructor_num_dict:
                            if full_name not in instructor_table_dict:
                                for tup in instructor_num_dict[full_name]:
                                    if dept == tup[1]:
                                        instructor_id = tup[0]
                                instructor_table_dict[full_name] = [last_name, \
                                                     first_name, instructor_id,dept]
                                link_table_class_list.append([instructor_id])
                        else:
                            # case II non-english character
                            name_found = False
                            sub_name_found = False
                            new_url = eval_url + row.find('a')['href']
                            new_req, new_page = get_request(new_url, cookie)
                            if new_req == None:
                                continue
                            ## blank page, then ignore and continue
                            elif new_page.find('p') == None:
                                continue
                            ## evluation not found, then continue
                            elif len(new_page.find('p').contents) <= 1:
                                continue
                            class_instructors = str(new_page.find('p').contents[2])
                            class_instructor_list = class_instructors.split(';')
                            for instructor in class_instructor_list:
                                instructor_sublist = []
                                for i in instructor.split(','):
                                    instructor_sublist += [j.strip().lower() for j in i.split()]
                                instructor_subset = set(instructor_sublist)
                                name_subset = set(name_list)
                                if (instructor_subset.issubset(name_subset)\
                                    or name_subset.issubset(instructor_subset))\
                                    and len(instructor_subset) != 0:
                                        name_found = True
                                        break
                                elif len(instructor_subset) != 0 \
                                        and len(name_subset) != 0:
                                    if name_list[0][0].lower() == instructor.lower().split()[0][0]\
                                            and name_list[1][0].lower() == instructor.lower().split()[1][0]:
                                        sub_name_found = True
                                        sub_instructor = instructor
                                    elif name_list[1][0].lower() == instructor.lower().split()[0][0]\
                                            and name_list[0][0].lower() == instructor.lower().split()[1][0]:
                                        sub_name_found = True
                                        sub_instructor = instructor
                            if name_found == False and sub_name_found == True:
                                print('Non-English Character met: instrcutor: {}'\
                                      .format(sub_instructor))
                                instructor = sub_instructor
                                name_found = True
                                    
                            if name_found == True:
                                instructor_name_list = instructor.split(',')
                                instructor_name_list = [i.strip().lower() \
                                        for i in instructor_name_list]
#                                print(instructor_name_list)
                                last_name = instructor_name_list[0]
                                first_name = instructor_name_list[1]
                                full_name = (', ').join(instructor_name_list)
                                for tup in instructor_num_dict[full_name]:
                                    if dept == tup[1]:
                                        instructor_id = tup[0]
                                instructor_table_dict[full_name] = [last_name, \
                                                     first_name, instructor_id, dept]
                                link_table_class_list.append([instructor_id])
                            else:
                                err_count += 1
                                last_name, first_name, instructor_id = 'Name not Found',\
                                'Name not Found', 99999
                                
                                instructor_table_dict[full_name] = [last_name, \
                                first_name, instructor_id, dept]
                                link_table_class_list.append([instructor_id])
                                print('Name not found: {}, Department:{}'\
                                      .format(name, dept))
                            
                    id_tracker.add(instructor_id)
                ## construct the link table
                if link_table_class_list != []:
                    for entry in link_table_class_list:
                        entry.extend([course_id, year, class_section, quarter])
                        link_table_list.append(entry)
                        
                ## construct the url list
                url_dict = {}
                url = eval_url + row.find('a')['href']
                url_dict['course_id'] = course_id
                url_dict['year'] = year
                url_dict['section'] = class_section
                url_dict['url'] = url
                url_dict['instructor'] = list(id_tracker)
                url_dict['dept'] = dept
                url_dict['quarter'] = quarter
                url_list.append(url_dict)
    # write course table
    if overwrite:
        outputfile = open('course_table.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for course_list in list(course_table_dict.values()):
            outputwriter.writerow(["|".join([str(i) for i in course_list])])
        outputfile.close()
        # write instructor table
        outputfile = open('instructor_table.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for instructor_list in list(instructor_table_dict.values()):
            outputwriter.writerow(["|".join([re.sub(r'[^\x00-\x7F]+',' ', str(i)) for i in instructor_list])])
        outputfile.close()
        # write link table
        outputfile = open('link_table.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for link_list in link_table_list:
            outputwriter.writerow(["|".join([str(i) for i in link_list])])
        outputfile.close()
    print(err_count)
    return course_table_dict, instructor_table_dict, link_table_list, url_list 


def create_ecvaluation_table(eval_url, cookie, dept_list, year_list, course_num_dict,\
                      instructor_num_dict, url_list, driver, user_name, password, overwrite = True):
    '''
    A fucntion to create the table for: average score of the instructors, comments
    of the insturctors
    '''
    course_eval_table = []
    ins_comm_table = []     ##store the comments
    ins_eval_table = []     ##store the evaluation score for each item
    ins_score_table = []    ##store the average score
    past_dept = ''
    start = time.time()
    for safe_index, url_dict in enumerate(url_list):
        # save the table every 200 items
        if safe_index // 200 == 0:
            with open('ins_comm_backup1', 'wb') as fp:
                pickle.dump(ins_comm_table, fp)
        # every one hour we relog into the site
        if time.time() - start > 3600:
            driver.quit()
            driver = webdriver.Firefox()
            driver.get("https://evaluations.uchicago.edu")
            cookie = relog_in(driver, eval_url, user_name, password)
            start = time.time()
        ## if the evluation table has a column for non response
        na_flag = False
        total_scores = []
        course_id, year, class_section, url, ins_list, cur_dept, quarter = url_dict['course_id'], \
                url_dict['year'], url_dict['section'], url_dict['url'], url_dict['instructor'],\
                        url_dict['dept'], url_dict['quarter']
        if cur_dept != past_dept:
            print('Create Evluation....: At {} year {}'.format(cur_dept, year))
            past_dept = cur_dept
        cur_req, cur_page = get_request(url, cookie)
        # if the request is bad
        if cur_req == None:
            continue
        
        page_paragraph = cur_page.find('p')
        tot_response = 0
        if page_paragraph != None:
            if len(page_paragraph.contents)>1:
                tot_response_lit = re.findall('\d+', str(page_paragraph.contents[-1]))
                if tot_response_lit != []:
                    tot_response = int(tot_response_lit[0])
        url_dict['tot_response'] = tot_response
        ## construct evaluation table
        header2 = cur_page.find_all('h2')
        tag = None
        for h in header2:
            if 'instructor' in h.text.lower():
                tag = h
        if tag == None:
            continue
        for i in range(5):
            if isinstance(tag, bs4.element.Tag):
                if tag.name == 'table':
                    break
            tag = tag.next_sibling
        if tag.name == 'table':
            compute_tr_score(tag, ins_score_table, total_scores, \
                             url_dict, ins_list, na_flag, True)
            for i in range(5):
                tag = tag.next_sibling
                try:
                    if 'explain' in tag.text.lower():
                        while tag.name!= 'table':
                            tag = tag.next_sibling
                            if tag == None:
                                break
                        if tag == None:
                            break
                        elif tag.name == 'table':
                            compute_tr_score(tag, ins_score_table, total_scores, \
                                    url_dict, ins_list, na_flag, False)
                        
                except:
                    continue
            ## compute avg_score -list
            counter = 0
            temp_total_score =0 
            for i, s in enumerate(total_scores):
                if isinstance(s, float) or isinstance(s, int):
                    temp_total_score += s
                    counter += 1
            if counter != 0:
                for ins_id in ins_list:
                    ins_eval_table.append([course_id, year, class_section, quarter, \
                                       ins_id, temp_total_score/counter, tot_response])
            else:
                for ins_id in ins_list:
                    ins_eval_table.append([course_id, year, class_section, quarter,\
                                       ins_id, 'No score', tot_response])
        
        ## construct comment table
        get_comment(cur_page, url_dict, ins_comm_table)
    with open('ins_comm_backup2', 'wb') as fp:
        pickle.dump(ins_comm_table, fp)
    if overwrite:
        outputfile = open('instructor_avgscore.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for t in ins_eval_table:
            outputwriter.writerow(["|".join([str(i) for i in t])])
        outputfile.close()   
        outputfile = open('instructor_score.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for t in ins_score_table:
            outputwriter.writerow(["|".join([str(i) for i in t])])
        outputfile.close()   
        with open('ins_comm_list', 'wb') as fp:
            pickle.dump(ins_comm_table, fp)
        
        outputfile = open('instructor_comments.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for t in ins_comm_table:
            try:
                outputwriter.writerow(["|".join([re.sub(r'[^\x00-\x7F]+',' ', str(i)) for i in t])])
            except:
                continue
        outputfile.close()   

        outputfile = open('instructor_comments_ascii.csv', "w", newline = "")
        outputwriter = csv.writer(outputfile)
        for t in ins_comm_table:
            try:
                outputwriter.writerow(["|".join([str(i) for i in t])])
            except:
                continue
        outputfile.close()   
        
    return ins_eval_table, ins_score_table, ins_comm_table
        
        
def compute_tr_score(tag, ins_score_table, total_scores, url_dict, ins_list, na_flag, check_first):
    '''
    A helper function to compute the average score for each criterion 
    of an instructor
    '''
    course_id, year, class_section, url, ins_list, quarter, tot_response = url_dict['course_id'], \
                url_dict['year'], url_dict['section'], url_dict['url'], \
                url_dict['instructor'], url_dict['quarter'], url_dict['tot_response']
    tag_tr_list = tag.find_all('tr')
    for i, row in enumerate(tag_tr_list):
        if i == 0 and check_first == True:
            scale_list = row.find_all('th')
            for scale in scale_list:
                if scale.text == 'N/A':
                    na_flag = True
        else:
            score_term = row.find_all('th')[0].text
            if score_term == '\xa0':
                continue
            score_list = row.find_all('td')
            if na_flag:
                score_list = score_list[1:]
            total_score = 0
            total_percent = 0
            for i, score in enumerate(score_list):
                temp_percent = re.findall("\d+", score.text)[0]
                if temp_percent != '':
                    temp_percent = int(temp_percent)
                    temp_score = (i + 1) * temp_percent
                # if the score is empty
                else:
                    temp_score = 0
                    temp_percent = 0
                total_percent += temp_percent
                total_score += temp_score
            if total_percent != 0:    
                avg_score = total_score / total_percent
            else:
                avg_score = 'No score'
            for instructor_id in ins_list:
                ins_score_table.append([course_id, year, \
                    class_section, quarter, instructor_id, score_term, avg_score, tot_response])
            ## update the list to compute average score
            total_scores.append(avg_score)
    return 
  

def get_comment(page, url_dict, ins_comm_table):
    '''
    A helper function to scrape all of the comments on one page
    '''
    course_id, year, class_section, url, ins_list, quarter = url_dict['course_id'], \
            url_dict['year'], url_dict['section'], url_dict['url'], \
            url_dict['instructor'], url_dict['quarter']
    comment_blocks = []
    headers = page.find_all('h3')
    for h in headers:
        text = h.text.lower()
        # identify the strength and weaknesses of an instructor
        crit = (('strong' in text) or ('weak' in text) or ('strength' in text)\
               or ('weakness' in text)) and 'instructor' in text
        if crit:
            comment_blocks.append(h)
    for comm_block in comment_blocks:
        for i in range(5):
            ## skip all of the line breaks
            if isinstance(comm_block, bs4.element.Tag):
                if comm_block.name == 'div':
                    break
                else:
                    comm_block = comm_block.next_sibling
            elif comm_block == None:
                break
            else:
                comm_block = comm_block.next_sibling
        if comm_block == None:
            continue
        comments = comm_block.find_all('li')
        for comm in comments:
            for instructor_id in ins_list:
                ins_comm_table.append([course_id, year, \
                            class_section, quarter, instructor_id, comm.text]) 
    return

def get_sql(file_name):
    '''
    A function to transfer the csv file for comments to sql db
    '''
    with open(file_name, 'rt') as fb:
        db_reader = csv.reader(fb, delimiter = '|')
        db_list = [ i for i in db_reader]
    for i, entry in enumerate(db_list):
        if len(entry) != 6:
            db_list[i] = tuple(entry[0].split('|'))
        if len(db_list[i]) != 6:
            temp_list = list(db_list[i])
            temp_list[5] = ' '.join(temp_list[i][5:])
            db_list[i] = tuple(temp_list[:6])
    con = sqlite3.connect("ins_comment.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE ins_comments (course_id int, year int, \
    class_section int, quarter int, instructor_id int, comments nvarchar(10000)\
    );")
    cur.executemany("INSERT INTO ins_comments (course_id, year, \
    class_section, quarter, instructor_id, comments\
    ) VALUES (?, ?, ?, ?, ?, ?);", db_list)
    con.commit()
    con.close()
    return
    
#cur.execute('SELECT * FROM ins_comments WHERE comments = NULL')


if __name__ == '__main__':
    ## Flags for calling functions
    course_compile = False
    instructor_compile = False
    main_table = False
    eval_url = 'https://evaluations.uchicago.edu/'
    # create a new Firefox session
    driver = webdriver.Firefox()
    #driver.implicitly_wait(30)
    driver.maximize_window()
    driver.get(eval_url)
    
    cookie, user_name, password = log_in(driver, eval_url)
    # navigate to the application home page
    driver.get("https://evaluations.uchicago.edu")
    dept_list, year_list = find_dept_year_list(eval_url, cookie)
    course_num_dict = {}
    if course_compile:
        course_num_dict = compile_course_num(eval_url, cookie, dept_list, year_list)
        with open('course_num.json', 'w') as f:
            json.dump(course_num_dict, f, ensure_ascii = False)
    if instructor_compile:
        count = 7853
        start, previous = time.time(), time.time()
        ## save the instructor dict for each department
        for i, dept in enumerate(dept_list):
            if time.time() - start > 3600 or time.time() - previous > 900:
                driver.quit()
                driver = webdriver.Firefox(executable_path = '/home/hluxi/FinalProject_cs/geckodriver')
                driver.get("https://evaluations.uchicago.edu")
                cookie = relog_in(driver, eval_url, user_name, password)
                start = time.time()
            previous = time.time()
            instructor_num_dict, count = compile_instructor_num(eval_url, \
                                        cookie, [dept], year_list, count)
            if i == 0:
                old_dict = {}
                counter = {}
            else:
                with open('instructor_num.json') as f:
                    old_dict = json.load(f)
                with open('counter.json') as f:
                    counter = json.load(f)
            for key, value in instructor_num_dict.items():
                old_list = old_dict.get(key, [])
                old_dict[key] = old_list + value
            counter[dept] = count
            with open('instructor_num.json', 'w') as f:
                json.dump(old_dict, f, ensure_ascii = True)
            with open('counter.json', 'w') as f:
                json.dump(counter, f, ensure_ascii = True)
    with open('course_num.json') as f:
        course_num_dict = json.load(f)
    with open('instructor_num.json') as f:
        instructor_num_dict = json.load(f)
    instructor_num_dict['Name not Found'] = [[99999, 'No Department']]
    if main_table:
        a, b, c, url_list = create_main_table(eval_url, cookie, dept_list, year_list, course_num_dict,\
                      instructor_num_dict)
        with open('outfile', 'wb') as fp:
            pickle.dump(url_list, fp)
    else:
        with open('outfile', 'rb') as fp:
            url_list = pickle.load(fp)
    create_ecvaluation_table(eval_url, cookie, dept_list, year_list, course_num_dict,\
                      instructor_num_dict, url_list, driver, user_name, password, overwrite = True)
        

    driver.quit()