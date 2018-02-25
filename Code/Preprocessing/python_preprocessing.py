#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: Alice Mee Seon Chung
"""

import os, re
import pandas as pd
import datetime
import nltk

# filter_wordsls = ['free trade agreeement','free trade' ,'liberalization',
#  'liberalize' 'labor', 'labor union', 'export', 'grow', 'growth', 'manufacturing',
#  'world','subsidy', 'protect', 'protection', 'economy', 'china','import', 
#  'competition', 'compete', 'rust belt','mexico', 'cheap', 'unemploy', 
#  'unemployment', 'adjustment', 'adjust' ,'wto', 'nafta', 'dumping', 'anti-dumping',
#  'trade','unfair']

rustbelts = ['New York', 'Pennsylvania', 'West Virginia', 'Ohio', 'Indiana', 'Michigan',
             'Illinois', 'Iowa', 'Wisconsin', 'Missouri']

rustbelts_ex = ['Pennsylvania', 'West Virginia', 'Ohio', 'Indiana', 'Michigan',
             'Illinois', 'Iowa', 'Wisconsin', 'Missouri']

dem = ['Barack Obama', 'Hillary Clinton', 'John Edwards', 'Bill Richardson',
      'Christopher Dodd', 'Joe Biden', 'Bernie Sanders',  "Martin O'Malley", 
      'Lincoln Chafee', 'Jim Webb']

rep = ['John McCain', 'Mike Huckabee', 'Mitt Romney', 'Rudy Giuliani',
      'Fred Thompson', 'Ron Paul', 'Newt Gingrich', 'Rick Santorum', 'Rick Perry',
      'Jon Huntsman', 'Michele Bachmann', 'Herman Cain', 'Tim Pawlenty',
       'Donald J. Trump', 'John Kasich', 'Ted Cruz', 'Marco Rubio', 'Ben Carson',
      'Jeb Bush', 'Chris Christie', 'Carly Fiorina', 'Rand Paul', 'George Pataki',
      'Lindsey Graham','Scott Walker', 'Bobby Jindal']

stops = nltk.corpus.stopwords.words('english')

rootDir = '../Data/'

d = {}
remarkls = []
interviewls = []
questionls = []
otherls = []
speechls = []
addressls = []
pe_dict = {2008:{}, 2012:{}, 2016:{}}

for dirName, subdirList, fileList in os.walk(rootDir) :
    print('Found directory: %s' % dirName)
    print(dirName)
    c = 0
    for fname in fileList:        
        if fname.endswith(".txt"):  
            filepath = os.path.join(dirName, fname)
            if dirName == '../Data/PE2008':  
                c += 1
                year = 2008
                d = pe_dict[year]
                speaker = fname[8:-4]
            else:
                c += 1
                year = fname[8:12]
                d = pe_dict[int(year)]
                speaker = fname[12:-4]
            if speaker in dem:
                partyid = 'Dem'
            if speaker in rep:
                partyid = 'Rep'
            d[speaker]={}
            with open(filepath, 'r', -1, "ISO-8859-1") as input_file:
                data = input_file.read()
                splited_speeches = data.split('\n\n\n')
                #print(splited_speeches)
                statement_num = 0
                for i in range(len(splited_speeches)):
                    statement_num += 1
                    one_speech = re.sub(r'\((?!k\))(.*?)\)', '', splited_speeches[i], flags= re.IGNORECASE)
                    one_speech_fin = re.sub(r'\[(.*?)\]', '', one_speech) 
                    t = one_speech_fin.replace('\x80\x94','').replace('\x80','').replace('\x94','').split('\n')
                    text = [item for item in t if item != '' if not item.startswith('To view')\
                            if not item.startswith('Citation:')]
                    whole_text = " ".join(text[2:])     
                    #whole_text5 = re.sub(r'[^\w\s]', '',whole_text.lower())
                    #tokens = nltk.tokenize.word_tokenize(whole_text5.lower())
                    #punc = [re.sub(r'[^\w]', '', word.lower()) for word in stops]
                    #whole_text4 = [word for word in tokens if word.lower() not in punc]
                    #fd = nltk.FreqDist(whole_text4)
                    if text != []:
                        title = text[0]
                        dateobj = datetime.datetime.strptime(text[1], '%B %d, %Y')
                        remarkls.append([speaker, title])
                        if 'remarks' in text[0].lower():
                            remarkls.append([speaker, title])
                            ttype = 'remarks'
                        elif 'speech' in text[0].lower():
                            speechls.append([speaker, title])
                            ttype = 'speech'
                        elif 'interview' in text[0].lower():
                            interviewls.append([speaker, title])
                            ttype = 'interview'
                        elif ('question' or 'q&a') in text[0].lower():
                            questionls.append([speaker, title])
                            ttype = 'question'
                        elif 'address' in text[0].lower():
                            addressls.append([speaker, title]) 
                            ttype = 'address'
                        else:
                            otherls.append([speaker, title])
                            ttype = 'others'
                                                
                        d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                    'Year':year, 'Whole':splited_speeches[i],
                                                     'Clean': whole_text,
                                                     'Text': text,
                                                     'Date':dateobj,
                                                    'Type': ttype,
                                                     'PartyID':partyid}
                                                    
                        #fdls.append(fd.most_common(10))      
                        for word in filter_wordsls:
                            num = len(re.findall(word, speech.lower()))
                            d[speaker][statement_num].update({word: num})         

# convert dictionary to dataframe
temp = {}
for year1, values1 in pe_dict.items():
    for author1, values2 in values1.items():
        for number, values3 in values2.items():
            #print(values3)
            temp.setdefault('Year1', []).append(year1)
            temp.setdefault('Author1', []).append(author1)
            temp.setdefault('No.', []).append(number)
            for key, value in values3.items():
                temp.setdefault(key, []).append(value)

df = pd.DataFrame(temp)

# filter by years
df08 = df[df['Year1'] == 2008]
df12 = df[df['Year1'] == 2012]
df16 = df[df['Year1'] == 2016]

# filter out duplicate speeches on every presidential elections
f08 = df08[(datetime.datetime(2005, 1, 1, 0, 0) <= df08['Date']) \
           & (df08['Date'] <= datetime.datetime(2008, 12, 31, 0, 0))]
f12 = df12[(datetime.datetime(2009, 1, 1, 0, 0) <= df12['Date']) \
           & (df12['Date'] <= datetime.datetime(2012, 12, 31, 0, 0))]
f16 = df16[(datetime.datetime(2013, 1, 1, 0, 0) <= df16['Date']) \
           & (df16['Date'] <= datetime.datetime(2016, 12, 31, 0, 0))]

refine = pd.concat([f08,f12,f16]).reset_index()

refine_fin  = refine[['Author', 'Author1', 'Clean', 'Date', 'No.', 'PartyID', 'Text',
                        'Title', 'Type', 'Whole', 'Year', 'Year1']]

#refine_fin.to_csv('../Data/df_180223.csv') 
#rdf = pd.read_csv('../Data/df_180223.csv')
# load file contains state information
adddf = pd.read_excel('../Data/df18022_addingstate_afternoon.xlsx', sheet_name='df18022_addingstate')
# merge and add state information
merged = refine_fin.merge(adddf, left_on=['Author','No.','Year'],
                right_on = ['Author','No.','Year'], how='left')

addingstatedf = merged[['Unnamed: 0', 'Author', 'Author1', 'Clean', 'Date', 'No.', 'PartyID',
                        'State','Abb','Text', 'Title_x', 'Type_x', 'Whole', 'Year', 'Year1', 
                        'index','Title_y', 'Type_y']]

addstate08 = addingstatedf[addingstatedf['Year1'] == 2008]
addstate12 = addingstatedf[addingstatedf['Year1'] == 2012]
addstate16 = addingstatedf[addingstatedf['Year1'] == 2016]

alldf = pd.concat([addstate08,addstate12,addstate16])

# load file contains swing state ratio information
swing  = pd.read_excel('../Data/swingstate_2008-2016.xlsx')
sw08 = swing[swing['year'] == 2008]
sw12 = swing[swing['year'] == 2012]
sw16 = swing[swing['year'] == 2016]
# merge with original dataframe and add swing_last ration information
statesw08 = alldf.merge(sw08, left_on=['Abb'],right_on = ['state'], how='left')
statesw08.rename(columns = {'swing_last':'swing_last_08'}, inplace = True)
statesw12 = statesw08.merge(sw12, left_on=['Abb'],right_on = ['state'], how='left')
statesw12.rename(columns = {'swing_last':'swing_last_12'}, inplace = True)
statesw16 = statesw12.merge(sw16, left_on=['Abb'],right_on = ['state'], how='left')
statesw16.rename(columns = {'swing_last':'swing_last_16'}, inplace = True)

alldf_sw = statesw16[['Year', 'Year1', 'Author', 'Author1', 'Clean', 'Date', 'No.', 'PartyID',
       'State', 'Abb', 'Title_x', 'swing_last_08', 'swing_last_12', 'swing_last_16']]

# add flag for Rustbelt regions
alldf_sw ['Rustbelt'] = np.where(alldf_sw["State"].isin(rustbelts_ex), 1, 0)
alldf_sw.rename(columns = {'Title_x':'Title'}, inplace = True)

################ FINAL DATAFRAME 
# export to csv file
alldf_sw.to_csv('../Data/alldf_180223.csv', index = False)
