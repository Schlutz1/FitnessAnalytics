'''
Fns for extraction and processing of weightlifting data
'''

# modules & imports
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
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

def make_uid(r):
    '''creates workout uid'''
    return str(int(r['Rotation'])) + "." + str(int(r['Workout'])) + "." + str(int(r['Week']))

def make_datetime(r):
    '''constructs datetime object for each workout'''
    if pd.notnull(r['Date']) :
        datetime_string = datetime.datetime.combine(r['Date'], r['Time'])
        return datetime_string

def make_projected_1rm(r):
    '''calculates a theoretical 1RM for each lift'''
    if pd.notnull(r['Actual Lift']) :
        reps, w = r['Actual Lift'].split('x')[0], r['Actual Lift'].split('x')[1]
        return f
    return None

def cleanWeighliftingActivities():
    ''' Cleans up raw data '''
    df = pd.read_excel(
        os.path.join('tmp', 'tmp_FY20 H1 Workout Tracker.xlsx'), 
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
    df['id'] = df.apply(make_uid, axis=1)
    df['timestamp'] = df.apply(make_datetime, axis=1)
    df['projected_1rm'] = df.apply(make_projected_1rm, axis=1)

    return df

def getWeighliftingActivities(weightlifting_conf):
    ''' Extract weightlifting activities & metadata from Google Sheets '''

    callEndpoint(weightlifting_conf)
    df_weightlifting = cleanWeighliftingActivities()

    return df_weightlifting