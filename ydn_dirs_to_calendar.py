import glob
import shutil, os
from os import path
import csv
import numpy as np; np.random.seed(sum(map(ord, 'calmap')))
import pandas as pd
import calmap
import re
import dateparser
from bs4 import BeautifulSoup
isoregex  = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])'
match_iso8601 = re.compile(isoregex).match

def validate_iso8601(str_val):
    try:            
        if match_iso8601( str_val ) is not None:
            return True
    except:
        pass
    return False


events = []


metadatafile = "ydn_metadata_2022-02.csv"
with open(metadatafile, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['isodate','title','cdoc','dir_location'])

for file_desc in glob.glob('./YaleDailyNews/YaleDailyNews/**/1.desc', recursive = True):
    dir_location = file_desc.replace('1.desc','').replace('./YaleDailyNews/YaleDailyNews/','')
    #print(dir_location)
    new_unique_filename = file_desc.split('/')[-2]
    #print(new_unique_filename)
    

    #print(file_desc)
    infile = open(file_desc,"r")
    contents = infile.read()
    soup = BeautifulSoup(contents,'lxml')
    try:
    	issuetitle = soup.find_all('title')[0].text
    except:
    	issuetitle = '[NO TITLE]'
    try:

        isodate = soup.find_all('date')[0].text            
        # print(isodate)
        if validate_iso8601(isodate):
        	events.append([str(isodate),1])
        else:
        	print('ERROR in ISO DATE ' + isodate )
        	print('Now trying alternate method to find a human-readable date in "' + issuetitle + '"')
        	potentialdate =  re.split(r'[The ]*Yale [Daily ]*News [Magazine ]*no\. [A-Z0-9]+ ',issuetitle)[-1]
        	print(potentialdate)
        	isodate = dateparser.parse(potentialdate).strftime("%Y-%m-%d")
        	print(isodate)
    except:
        print('error paring date')
        with open('errors.txt', 'a') as errorlog:
        	errorlog.write('File "' + dir_location + '1.desc" could not be parsed for an isodate (retunred "' + isodate + '"). Title tag was "' + issuetitle + '."\n')

  
    with open(metadatafile, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([isodate,issuetitle,new_unique_filename,dir_location])

print(events)

df = pd.DataFrame(events, columns =  ['date','issue_exists'])
print(df)
df['date'] = pd.to_datetime(df['date'])

df.set_index('date',inplace=True)


fig = calmap.calendarplot(df['issue_exists'], how='sum', yearlabel_kws={'color':'black','rotation':0,'labelpad':60}, cmap='Reds', \
						daylabels='MTWTFSS', linecolor='black', linewidth=0.5, fig_kws=dict(figsize=(30,120), dpi=72),vmax=1)
fig[0].savefig('test.png')




