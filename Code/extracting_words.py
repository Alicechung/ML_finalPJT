import os, re
from geotext import GeoText
import pandas as pd

filter_wordsls = ['free trade agreeement','free trade' ,'liberalization', 'liberalize' 'labor', 'labor union',
'export', 'grow', 'growth', 'manufacturing' ,'world','subsidy', 'protect', 'protection', 
'economy', 'china','import', 'competition', 'compete', 'rust belt','mexico', 
'cheap', 'unemploy', 'unemployment', 'adjustment', 'adjust' ,'wto', 'nafta', 'dumping', 'anti-dumping']

rootDir = '../Data/'

#for dirName, subdirList, fileList in os.walk(rootDir) :

d = {}
#c = 0
remarkls = []
interviewls = []
questionls = []
otherls = []
speechls = []
addressls = []
r = 0
i = 0
q = 0
o = 0
s = 0
#statement_num = 0
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
            d[speaker]={}
            with open(filepath, 'r', -1, "ISO-8859-1") as input_file:
                data = input_file.read()
                splited_speeches = data.split('\n\n\n')
                statement_num = 0
                for i in range(len(splited_speeches)):
                    statement_num += 1
                    speech = splited_speeches[i]
                    #d[speaker][statement_num] = {}

                    text_first = speech.split('\n')
                    text = [item for item in text_first if item != '']
                    if text != []:
                        title = text[0]
                        if 'remarks' in text[0].lower():
                            remarkls.append([speaker, title])
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text, 
                                                         'Type': 'remarks', 'City':city}
                        elif 'speech' in text[0].lower():
                            speechls.append([speaker, title])
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text, 
                                                         'Type': 'speech','City':city}
                        elif 'interview' in text[0].lower():
                            interviewls.append([speaker, title])
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text,
                                                         'Type': 'interview','City':city }
                        elif ('question' or 'q&a') in text[0].lower():
                            questionls.append([speaker, title])
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text,
                                                         'Type': 'question','City':city}
                        elif 'address' in text[0].lower():
                            addressls.append([speaker, title]) 
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text,
                                                         'Type': 'address','City':city}
                        else:
                            otherls.append([speaker, title])
                            places = GeoText(title)
                            city_name = places.cities
                            if len(city_name) == 0 :
                                city = 0
                            else:
                                city = city_name[0]
                            d[speaker][statement_num] = {'Author': speaker, 'Title': title,
                                                   'Year':year, #'Text': text,
                                                         'Type': 'others','City':city}
                        for word in filter_wordsls:
                            num = len(re.findall(word, speech.lower()))
                            d[speaker][statement_num].update({word: num})

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
#print(pd.DataFrame(temp))

df = pd.DataFrame(temp)
df.to_csv('../Data/primaryresult_words_count_rev.csv')