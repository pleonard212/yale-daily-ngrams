import glob
import shutil, os
from os import path
import csv
import re
import dateparser
from bs4 import BeautifulSoup

import sys


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
    dir_location = file_desc.replace('index.desc','').replace('./YaleDailyNews/YaleDailyNews/','')
    full_dirlocation = file_desc.replace('index.desc','')
    #print(dir_location)
    new_unique_filename = file_desc.split('/')[-2]
    #print(new_unique_filename)
    
    # try:
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
            isodate = isodate
        else:
            #print('ERROR in ISO DATE ' + isodate )
            potentialdate =  re.split(r'The Yale News no\. [0-9]+ ',issuetitle)[-1]
            #print('Now trying alternate method to find a human-readable date in "' + issuetitle + '": ' + potentialdate)
            # potentialdate =  re.split(r'[The ]*Yale [Daily ]*News [Magazine ]*no\. [A-Z0-9]+ ',issuetitle)[-1]


            #print(potentialdate)
            isodate = dateparser.parse(potentialdate).strftime("%Y-%m-%d")
            print(isodate)
    except:
        print('error paring date')
        with open('errors.txt', 'a') as errorlog:
            errorlog.write('File "' + dir_location + '1.desc" could not be parsed for an isodate (returned "' + isodate + '"). Title tag was "' + issuetitle + '."\n')


    ### Normalized Storage section
    normalized_base = 'normalized_storage'
    duplicates_base = 'normalized_duplicates'
    normalized_year = isodate[0:4]
    normalized_semester_digits = int(isodate[6:7])
    if normalized_semester_digits >= 7:
        print('Assigning ' + isodate + ' to the Fall ' + normalized_year + ' Semester.')
        normalized_academic_year = normalized_year + '-' + str(int(normalized_year) +  1)
    else:
        print('Assigning ' + isodate + ' to the Spring ' + normalized_year + ' Semester.')
        normalized_academic_year = str(int(normalized_year) - 1) + '-' + normalized_year

    dir_to_create = os.path.join(normalized_base, normalized_academic_year)
    if not os.path.exists(dir_to_create):
        print('Creating ' + dir_to_create)
        os.makedirs(dir_to_create)
    normalized_destination = os.path.join(dir_to_create, (isodate + '_00'))
    print('Moving ' +  full_dirlocation + ' to ' + normalized_destination)
    if os.path.isdir(normalized_destination):
        print('That directory exits already.')
        issue_count = []
        for existing_dir in glob.glob(os.path.join(duplicates_base, normalized_academic_year,(isodate + '*'))):
            issue_count.append(existing_dir[-2:])
            print('Found issue ' + existing_dir[-2:] )
        try:
            highest_issue_count = max(issue_count)
        except:
            highest_issue_count = 0
        print('Highest issue is ' +  str(highest_issue_count))
        new_issue_count = int(highest_issue_count) + 1
        print('Creating issue ' + str(new_issue_count))
        dupedir_to_create = os.path.join(duplicates_base, normalized_academic_year)
        normalized_duplicatedestination = os.path.join(dupedir_to_create,(isodate + '_' + str(new_issue_count).zfill(2)))
        print('Moving ' +  full_dirlocation + ' to ' + normalized_duplicatedestination)
        if not os.path.exists(os.path.join(dupedir_to_create)):
            print('Creating ' + dupedir_to_create)
            os.makedirs(dupedir_to_create)
        print('doing a duplicates move')
        shutil.move(full_dirlocation, normalized_duplicatedestination)
    else:
        print('doing a normal move')
        shutil.move(full_dirlocation, normalized_destination)

