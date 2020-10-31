'''
Pipeline for ETL of fitness data

'''

# imports & modules

import pandas as pd
import datetime
import os, sys

import strava

# system globals
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)


class FitnessHandler():
    ''' Wrapper for pipeline methods '''

    def __init__(self):
        self.current_date = datetime.datetime.now()

    def getRunning(self):
        ''' Extracts running data from Strava '''
        df_strava = strava.getStravaActivities()
        return df_strava

    def runPipeline(self):
        ''' Executes pipeline '''
        print("Pipeline executing: {date}".format(
            date = self.current_date
        ))
        return self.getRunning()


if __name__ == "__main__":
    pipeline = FitnessHandler()
    df_fitnessData = pipeline.runPipeline()
    df_fitnessData.to_csv(
        os.path.join(abs_path, '..', 'extracts', 'stravaExtract.csv'), 
        index=False
    )
