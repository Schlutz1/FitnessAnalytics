import requests as r
import pandas as pd
import polyline
import time
import json
import ast
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# globals
abs_path = os.path.dirname(os.path.abspath(__file__))
resources_path = os.path.join(abs_path, '..', 'resources')

strava_lookup = {
    "start_date_local" : "timestamp",
    "name" : "notes"
}

def getStravaSecrets() :
    '''fn to return strava secrets'''
    strava_secrets = {
        "strava_pw": os.getenv("STRAVA_PW"),
        "strava_user" : os.getenv("STRAVA_USER"),
        "strava_client_id": os.getenv("STRAVA_CLIENT_ID"),
        "strava_client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
        "response_type": "code",
        "scope" : "activity:read_all",
        "redirect_uri" : "http://localhost/exchange_token"
    }
    return strava_secrets
    
def completeStravaAuth(strava_conf, strava_secrets, auth_url) :
    '''
    fn to complete strava auth flow
    : param strava_secrets: JSON object of all config
    : param strava_secrets: parameterised uri 
    : return resp_url:
    NOTE: this is shockingly bad, and literally the worst way to do this possible - please fix
    '''
    
    # attempt to automate in selenium (PLEASE FIX)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(
        executable_path=os.path.join(resources_path, 'chromedriver'),
        options = chrome_options
    )
    time.sleep(1)
    driver.get(auth_url)


    time.sleep(2)
    email_element = driver.find_element_by_name("email")
    email_element.send_keys(strava_secrets['strava_user'])

    pw_element = driver.find_element_by_name("password")
    pw_element.send_keys(strava_secrets['strava_pw'])

    login_element = driver.find_element_by_id("login-button")
    login_element.click()

    time.sleep(1)
    auth_element = driver.find_element_by_id("authorize")
    auth_element.click()

    resp_url = driver.current_url
    driver.quit()

    # extract code from resp url
    code = resp_url.split("code=")[1].split("&")[0]
    tok_url = strava_conf['URL_TOKEN'].format(
        client_id = strava_secrets['strava_client_id'],
        client_secret = strava_secrets['strava_client_secret'],
        code = code
    )
    
    # post to tok_url and extract access_token
    tok_resp = r.post(tok_url)
    if tok_resp.status_code != 200 :
        return ""
    
    access_token = tok_resp.json()['access_token']
    f_access_token = "access_token={access_token}".format(access_token = access_token)
    
    return f_access_token

def formatStravaActivities(df, strava_conf):
    ''' Fn to format strava activities to allow concat with other endpoints '''
    df = df[strava_conf['FIELDS']]
    df.rename(columns=strava_lookup, inplace=True)
    df['exercise'] = 'Running'
    return df

def getStravaActivities(strava_conf) :
    '''
    fn to return dataframe of all strava activities
    : param strava_conf: strava conf details
    '''

    # globals
    strava_secrets = getStravaSecrets()

    auth_url = strava_conf['URL_AUTH'].format(
        client_id = strava_secrets['strava_client_id'],
        response_type = strava_secrets['response_type'],
        redirect_uri = strava_secrets['redirect_uri'],
        scope = strava_secrets['scope']
    )
    
    f_access_token = completeStravaAuth(strava_conf, strava_secrets, auth_url)

    df_activities = pd.DataFrame()
    page = 1

    # paginate across Strava data                              
    while True:
        resp = r.get(strava_conf['URL_ACTIVITIES'] + '?' + f_access_token + '&per_page=50' + '&page=' + str(page))
        _dict = resp.json()

        if len(_dict) == 0 :
            break

        else :
            df_activities = df_activities.append(pd.DataFrame(_dict)) 
            page += 1

    return formatStravaActivities(df_activities, strava_conf)

def decodePolylineData(mapData):
    ''' Decodes polyline data into latlong array '''

    if isinstance(mapData, str):
        mapData = ast.literal_eval(mapData)

    return polyline.decode(mapData['summary_polyline'])

def filterAnomalousPolylineData(df):
    ''' 
    Implements a filtering fn for strava polyline data
    Strava GPS likes to 'blip' and show erroneous jumps
    Fn removes junk points to smooth out mapping in Tableau
    Typically a ∆lat or ∆lng ≥ ±0.002 is erroneous
    '''
    
    df[['lat_diff', 'lng_diff']] = df[['lat', 'lng']].diff(axis=0)
    df_filtered = df[
        (abs(df['lat_diff']) <= 0.002 ) &
        (abs(df['lng_diff']) <= 0.002 )
    ]
    return df_filtered


def generatePolylineDf(df):
    ''' Generate df for polyline data '''

    df_polyline = pd.DataFrame()
    for idx, grp in df.groupby(['id', 'timestamp', 'map']):
        decodedPolylineData = decodePolylineData(idx[2])
        df_run = pd.DataFrame(decodedPolylineData, columns=['lat', 'lng'])
        df_run.reset_index(inplace=True)
        df_run['timestamp'] = idx[1]
        df_run['id'] = idx[0]
        
        df_polyline = df_polyline.append(df_run)
    
    df_polyline_filtered = filterAnomalousPolylineData(df_polyline)
    print(df_polyline_filtered.shape)
    return df_polyline_filtered