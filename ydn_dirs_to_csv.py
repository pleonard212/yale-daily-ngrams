import glob
import shutil, os
from os import path
import csv
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


metadatafile = "ydn_metadata_2022-02.csv"
with open(metadatafile, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['isodate','cdoc','dir_location'])

for file_desc in glob.glob('./YaleDailyNews/YaleDailyNews/**/index.desc', recursive = True):
    dir_location = file_desc.replace('1.desc','').replace('./YaleDailyNews/YaleDailyNews/','')
    print(dir_location)
    new_unique_filename = file_desc.split('/')[-2]
    print(new_unique_filename)
    
    # try:
    print(file_desc)
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
            isodate = isodate
        else:
            print('ERROR in ISO DATE ' + isodate )
            potentialdate =  re.split(r'The Yale News no\. [0-9]+ ',issuetitle)[-1]
            print('Now trying alternate method to find a human-readable date in "' + issuetitle + '": ' + potentialdate)
            # potentialdate =  re.split(r'[The ]*Yale [Daily ]*News [Magazine ]*no\. [A-Z0-9]+ ',issuetitle)[-1]


            print(potentialdate)
            isodate = dateparser.parse(potentialdate).strftime("%Y-%m-%d")
            print(isodate)
    except:
        print('error paring date')
        with open('errors.txt', 'a') as errorlog:
            errorlog.write('File "' + dir_location + '1.desc" could not be parsed for an isodate (returned "' + isodate + '"). Title tag was "' + issuetitle + '."\n')



    with open(metadatafile, 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([isodate,new_unique_filename,dir_location])

