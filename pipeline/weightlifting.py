'''
Fns for extraction and processing of weightlifting data
'''

# modules & imports
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import pandas as pd
import datetime
import os, sys

# globals
gauth = GoogleAuth()
drive = GoogleDrive(gauth)
abs_path = os.path.dirname(os.path.abspath(__file__))

mimetypes = {
    'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # Drive Document files as MS Word files.
    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # Drive Sheets files as MS Excel files.
}

exercise_lookup = {
    'Bench Press',
    'Deadlifts',
    'Shoulder Press',
    'Squat',
    'Snatch',
    'Clean & Jerk'
}

def callEndpoint(weightlifting_conf):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        
        if file1['title'] == weightlifting_conf['FILE']:
            
            download_mimetype = None
            if file1['mimeType'] in mimetypes:
                download_mimetype = mimetypes[file1['mimeType']]

            # write out to .xlsx as tmp file locally
            title = file1['title']
            file1.GetContentFile(
                os.path.join(abs_path, 'tmp', f'tmp_{title}.xlsx'),
                mimetype=download_mimetype
            )

def makeUID(r):
    '''creates workout uid'''
    return str(int(r['Rotation'])) + "." + str(int(r['Workout'])) + "." + str(int(r['Week']))

def makeDatetime(r):
    '''constructs datetime object for each workout'''
    if pd.notnull(r['Date']) :
        datetime_string = datetime.datetime.combine(r['Date'], r['Time'])
        return datetime_string

def makeProjected1RM(r):
    '''
    calculates a theoretical 1RM for each lift
    https://en.wikipedia.org/wiki/One-repetition_maximum#Calculating_1RM

    currently calculating submaximal 1rm using Epley formula
    '''
    if pd.notnull(r['Actual Lift']):
        reps, w = r['Actual Lift'].split('x')[0], r['Actual Lift'].split('x')[1]
        return float(w) * (1 + (int(reps) / 30))
    return None

def cleanWeightliftingActivities():
    ''' Cleans up raw data '''
    df = pd.read_excel(
        os.path.join('tmp', 'tmp_Workout Tracker.xlsx'), 
        skiprows=3
    )
    # create uid
    df[['Rotation', 'Workout']] = df[['Rotation', 'Workout']].fillna(method='ffill')

    # retain populated exercise data
    exercise_map = df['Exercise'].apply(lambda x: True if x in exercise_lookup else False)
    df = df[
        (exercise_map==True) &
        (df['Week'].isna()!=True) &
        (df['Actual Lift'].isna()!=True)
    ]

    # generate metadata
    df['id'] = df.apply(makeUID, axis=1)
    df['timestamp'] = df.apply(makeDatetime, axis=1)
    df['projected_1rm'] = df.apply(makeProjected1RM, axis=1)

    return df

def formatWeightliftingActivities(df, weightlifting_conf):
    ''' Fn to format weighlfting activities to allow concat with other endpoints '''
    df = df[weightlifting_conf['FIELDS']]
    return df

def getWeightliftingActivities(weightlifting_conf):
    ''' Extract weightlifting activities & metadata from Google Sheets '''
    callEndpoint(weightlifting_conf)
    df_weightlifting = cleanWeightliftingActivities()

    return formatWeightliftingActivities(df_weightlifting, weightlifting_conf)