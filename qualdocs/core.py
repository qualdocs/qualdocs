from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from collections import Counter

import json
import pandas as pd
import numpy as np

import re 

def get_service(client_secret=None):
    """
    Returns a service object for use with Drive API queries based on the contents of ~/.credentials/
    """


    credentials = get_credentials(client_secret)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    return service


def get_file_ids(service, search=None, max_files=250):
    """
    Get a dictionary of filenames:file_ids from the authenticated Drive account. 
    Can filter with search string. Returns / searches through most recent 250 files by default.

    Returns:
        file_ids, a dictionary of filenames:file_ids    
    """


    file_ids = {}

    results = service.files().list(
        pageSize=max_files,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
        return None


    for item in items:
        #print('{0} ({1})'.format(item['name'], item['id']))
        if search is None or item['name'].find(search) > 0:
            file_ids[item['name']] = item['id']

    return file_ids

def is_interactive():
    "Is python running in interactive"

    import __main__ as main
    return not hasattr(main, '__file__')

def get_credentials(client_secret=None):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    import sys
    sys.argv=['']


    SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

    if client_secret:
        CLIENT_SECRET_FILE = client_secret
    else:
        CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Drive API Python Quickstart'

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:

        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_json_dict(service, file_ids):
    """
    Gets comments from the API for the file_ids.

    Parameters:
        service, the API service object
        file_ids, a dictionary of filenames:file_ids, returned by get_file_ids()
    Returns: 
        c_json_dict, a dictionary of json responses for each comment
    """


    c_json_dict = {}

    for name, file_id in file_ids.items():
        service_c = service.comments()
        c_json_dict[name] = service_c.list(pageSize=100,
                                           fileId=file_id,
                                           fields="comments,kind,nextPageToken").execute()

    return c_json_dict



def strip_list(input_list):
    """
    Strips whitespace for all individual strings in a list
    Parameters:
        input_list, a list of strings
    Returns:
        output_list, a list of strings

    """

    output_list = []
    for item in input_list:
        output_list.append(item.strip())
    return output_list


def process_code(rawcode, text, code_replace_dict=None):
    """
    Helper function to parse a single code and quoted text to support the hierarchical index.
    Used by json_to_df(), not usually called directly by users.

    Parameters:
        rawcode, a string containing the text of the code (the comment text)
        text, a string containing the quoted text (the document text that is coded)
        code_replace_dict, a dictionary of strings (from:to) for renaming codes
    Returns:
        return_list, a list of tuples (code, text) for each unique code

    Usage:
        process_code("top: subcode1, subcode2", "quoted text")

        [('top: subcode1', 'quoted text'), ('top: subcode2', 'quoted text')]

    """

    text = text.replace("&#39;", "'")
    rawcode = rawcode.lower()
    #print("rawcode before: ", rawcode)

    if code_replace_dict is not None:

        replace_pattern = re.compile(r'\b(' + '|'.join(code_replace_dict.keys()) + r')\b')
        rawcode = replace_pattern.sub(lambda x: code_replace_dict[x.group()], rawcode)

    rawcode_sep = rawcode.split(":")
    num_parts = len(rawcode_sep)
    output_list = []
    
    if num_parts == 1:
        output_list.append((rawcode, text))
        return output_list
    
    if num_parts == 2:
        rawcode_sep = strip_list(rawcode_sep)
        
        if rawcode_sep[1].find(",") == -1:
            output_list.append((rawcode, text))
            return output_list
        
        else:
            return_list = []
            for item in strip_list(rawcode_sep[1].split(",")):
                code_concat = rawcode_sep[0] + ": " + item
                return_list.append((code_concat, text))
            return return_list
        
    if num_parts == 3:
        
        rawcode_sep = strip_list(rawcode_sep)
        main_code = rawcode_sep[0]
        subcode = rawcode_sep[1]
        sub_subcode = rawcode_sep[2]
        
        if sub_subcode.find(",") == -1:
            output_list.append((rawcode, text))
            return output_list

        else:
            return_list = []
            for item in strip_list(sub_subcode.split(",")):
                code_concat = main_code + ": " + subcode + ": "+ item
                return_list.append((code_concat, text))
            return return_list



def json_to_df(comments_json_dict, code_replace_dict=None):
    """
    Converts a dictionary of JSON responses from the API to a pandas dataframe
    with a hierarchical index.

    Parameters:
        comments_json_dict,
        code_replace_dict, optional dict of strings (from:to) for renaming codes
    Returns:
        codes_df, a pandas dataframe of grouped codes, quoted text, and metadata
    """


    codes_df = pd.DataFrame(columns=["code","subcode","sub_subcode", "name", "text", "comment_id", "coder"])

    for name, comments_json in comments_json_dict.items():

        for comment in comments_json['comments']:

            coded_text = comment['quotedFileContent']['value']
            raw_codes = comment['htmlContent']
            comment_id = comment['id']
            comment_author = comment['author']['displayName']

            #print(raw_codes)

            if raw_codes.find("<br>") == -1:

                process_result = process_code(raw_codes, coded_text, code_replace_dict)
                #print(process_result)
                for result in process_result:

                    codes_dict = {'code':result[0], 'name':name, 'text':result[1], 'comment_id': comment_id, "coder":comment_author}
                    codes_df = codes_df.append(pd.Series(codes_dict), ignore_index=True)    

            else:
                codes = raw_codes.split("<br>")
                for code in codes:

                    process_result = process_code(code, coded_text, code_replace_dict)

                    for result in process_result:

                        codes_dict = {'code':result[0], 'name':name, 'text':result[1], 'comment_id': comment_id, "coder":comment_author}
                        codes_df = codes_df.append(pd.Series(codes_dict), ignore_index=True)

    for row, items in codes_df.iterrows():
        #print(items['code'].split(":"))
        count = 0
        
        code_split = items['code'].split(":")
        
        for i in code_split:
            if count == 0:
                codes_df.ix[row]['code'] = i
            elif count == 1:
                codes_df.ix[row]['subcode'] = i
            elif count == 2:
                codes_df.ix[row]['sub_subcode'] = i
            else:
                assert True is False
            count = count + 1

    codes_df = codes_df.replace(np.nan, "")

    codes_df = codes_df.set_index(['code', 'subcode', 'sub_subcode', 'name']).sort_index()

    return codes_df
    

def get_code_list(codes_df):
    """
    Process dataframes to return  of lists of codes by level

    Parameters:
        codes_df, a dataframe of codes generated by json_to_df()
    Returns:
        code_list, a list of concatenated strings for each level of coded text
    """

    code_list = []

    for row in codes_df.iterrows():
        code_concat = ""
        for code in row[0][0:3]:
            if code != '':
                code_concat += code + ":"
                
        # remove trailing colon if exists        
        if code_concat[-1] == ':':
            code_concat = code_concat[0:-1]
            
        code_list.append(code_concat)
        
    
    return code_list
        
def get_code_counts(codes_df):
    """
    Counts the number of unique concatenations of codes in levels. 

    TODO: Support counting higher level codes independently of subcodes

    Parameters:
        codes_df, a dataframe of codes generated by json_to_df()
    Returns:
        code_list_counter, a Counter (extends dict) of counts for codes    

    """

    code_list = get_code_list(codes_df)

    code_list_counter = Counter(code_list)



