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

def getWeighliftingActivities(weightlifting_conf):
    ''' Extract weightlifting activities & metadata from Google Sheets '''

    callEndpoint(weightlifting_conf)