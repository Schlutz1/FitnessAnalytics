'''
Pipeline for ETL of fitness data

'''

# imports & modules
import pandas as pd
import datetime
import os, sys
import json

import strava
import settings

# system globals
settings.getEnv()
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)


class FitnessHandler():
    ''' Wrapper for pipeline methods '''

    def __init__(self):
        ''' globals for wrapper '''
        with open(os.path.join('..', 'conf', 'endpoints.json')) as conf:
            self.endpoint_conf = json.load(conf)
        
        self.current_date = datetime.datetime.now()

    def getRunning(self):
        ''' Extracts running data from Strava '''
        df_strava = strava.getStravaActivities(self.endpoint_conf['STRAVA'])
        return df_strava

    def getWeightlifting(self):
        ''' Extracts weightlifting data from Google Sheets '''
        return None

    def runPipeline(self):
        ''' Executes pipeline '''
        print("Pipeline executing: {date}".format(
            date = self.current_date
        ))
        return self.getRunning()


if __name__ == "__main__":

    # run pipeline
    pipeline = FitnessHandler()
    df_fitnessData = pipeline.runPipeline()
    df_fitnessData.to_csv(
        os.path.join(abs_path, '..', 'extracts', 'stravaExtract.csv'), 
        index=False
    )
