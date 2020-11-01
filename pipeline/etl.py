'''
Pipeline for ETL of fitness data
Currently implements pipelines for:
* Running data, from Strava API
* Weighlifting data, from Google Sheets
'''

# imports & modules
import pandas as pd
import datetime
import os, sys
import json

import weightlifting
import settings
import tableau
import strava

# system globals
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)
settings.getEnv()


class FitnessHandler():
    ''' Wrapper for pipeline methods '''

    def __init__(self):
        ''' globals for wrapper '''
        self.current_date = datetime.datetime.now()
        with open(os.path.join('..', 'conf', 'endpoints.json')) as conf:
            self.endpoint_conf = json.load(conf)

    def extractStravaData(self):
        ''' Extracts running data from Strava '''
        df_strava = strava.getStravaActivities(self.endpoint_conf['STRAVA'])
        return df_strava

    def extractWeightliftingData(self):
        ''' Extracts weightlifting data from Google Sheets '''
        df_weightlifting = weightlifting.getWeighliftingActivities(self.endpoint_conf['WEIGHTLIFTING'])

    def transformFitnessData(self):
        ''' Merge datasets together '''
        return None

    def loadFitnessData(self):
        ''' Loads fitness data into Tableau .hyper format '''
        return None

    def runPipeline(self):
        ''' Executes pipeline '''
        print("Pipeline executing: {date}".format(date = self.current_date))

        if self.endpoint_conf['PIPELINE']['STRAVA']:
            df_strava = self.extractStravaData()

        if self.endpoint_conf['PIPELINE']['WEIGHTLIFTING']:
            df_weightlifting = self.extractWeightliftingData()


if __name__ == "__main__":

    pipeline = FitnessHandler()
    pipeline.runPipeline()
