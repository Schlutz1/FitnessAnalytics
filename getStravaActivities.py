import requests as r
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
import json
import os, sys


def getStravaSecrets() :
    '''fn to return strava secrets'''
    with open('./stravaSecrets.json') as json_file:
        strava_secrets = json.load(json_file)

    strava_secrets["redirect_uri"] = 'http://localhost/exchange_token'
    strava_secrets["scope"] = 'activity:read_all'
    strava_secrets["response_type"] = 'code'
        
    return strava_secrets
    
    
def completeStravaAuth(strava_secrets, auth_url) :
    '''
    fn to complete strava auth flow
    : param strava_secrets: JSON object of all config
    : param strava_secrets: parameterised uri 
    : return resp_url:
    NOTE: this is shockingly bad, and literally the worst way to do this possible
    '''
    
    # attempt to automate in selenium

    driver = webdriver.Chrome()
    driver.get(auth_url)


    time.sleep(1)
    email_element = driver.find_element_by_name("email")
    email_element.send_keys(strava_secrets['email'])

    pw_element = driver.find_element_by_name("password")
    pw_element.send_keys(strava_secrets['password'])

    login_element = driver.find_element_by_id("login-button")
    login_element.click()

    time.sleep(1)
    auth_element = driver.find_element_by_id("authorize")
    auth_element.click()

    resp_url = driver.current_url
    driver.quit()

    # extract code from resp url
    code = resp_url.split("code=")[1].split("&")[0]
    tok_url = 'https://www.strava.com/oauth/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_typeauthorization_code'.format(
        client_id = strava_secrets['client_id'],
        client_secret = strava_secrets['client_secret'],
        code = code
    )
    
    # post to tok_url and extract access_token
    tok_resp = r.post(tok_url)
    if tok_resp.status_code != 200 :
        return ""
    
    access_token = tok_resp.json()['access_token']
    f_access_token = "access_token={access_token}".format(access_token = access_token)
    
    return f_access_token
    
def findStravaActivities() :
    '''fn to return dataframe of all strava activities'''
    
    # globals
    activites_url = "https://www.strava.com/api/v3/activities"
    strava_secrets = getStravaSecrets()
    
    if len(strava_secrets) > 0 :
    
        auth_url = 'http://www.strava.com/oauth/authorize?client_id={client_id}&response_type={response_type}&redirect_uri={redirect_uri}&scope={scope}'.format(
            client_id = strava_secrets['client_id'],
            response_type = strava_secrets['response_type'],
            redirect_uri = strava_secrets['redirect_uri'],
            scope = strava_secrets['scope']
        )
        
        f_access_token = completeStravaAuth(strava_secrets, auth_url)

        df_activities = pd.DataFrame()
        page = 1
                                            
        while True:

            # get page of activities from Strava
            resp = r.get(activites_url + '?' + f_access_token + '&per_page=50' + '&page=' + str(page))
            _dict = resp.json()

            if len(_dict) == 0 :
                break

            else :
                df_activities = df_activities.append(pd.DataFrame(_dict)) 
                page += 1

        return df_activities
        
        
    else :
        return pd.DataFrame()