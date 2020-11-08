'''
Pipeline for ETL of fitness data
Currently implements pipelines for:
* Running data, from Strava API
* Weighlifting data, from Google Sheets
'''

# imports & modules
from datetime import datetime, date
import pandas as pd
import os, sys
import json
import time

import weightlifting
import settings
import tableau
import strava

# system globals
abs_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abs_path)
settings.getEnv()

extract_path = os.path.join(abs_path, '..', "extracts")
conf_path = os.path.join(abs_path, '..', "conf")

class FitnessHandler():
    ''' Wrapper for pipeline methods '''

    def __init__(self):
        ''' globals for wrapper '''
        self.pipeline_start = datetime.now()
        with open(os.path.join(conf_path, 'endpoints.json')) as conf:
            self.endpoint_conf = json.load(conf)

    def extractStravaData(self):
        ''' Extracts running data from Strava '''
        df_strava = strava.getStravaActivities(self.endpoint_conf['STRAVA'])
        return df_strava

    def extractWeightliftingData(self):
        ''' Extracts weightlifting data from Google Sheets '''
        df_weightlifting = weightlifting.getWeightliftingActivities(self.endpoint_conf['WEIGHTLIFTING'])
        return df_weightlifting

    def cleanFitnessData(self, df):
        ''' Standardizes dataframe format for concatting '''
        cols_new = [col.replace(" ", "_").lower() for col in list(df)]
        df.columns = cols_new

        if 'pipeline_date' not in list(df):
            df['pipeline_date'] = self.pipeline_start

        df.drop_duplicates(subset=['id', 'exercise'], inplace=True)
        df.set_index(['id', 'exercise'], inplace=True)

        return df

    def loadFitnessData(self, df, analysis_type):
        ''' Loads fitness data into Tableau .hyper format '''
        tableau.makeConversion(df, self.endpoint_conf['TABLEAU']['FILES'][analysis_type])
        tableau.cleanLogs()


    def runPipeline(self):
        ''' Executes pipeline '''
        print("Pipeline executing: {date}".format(date = self.pipeline_start))

        df_fitness = pd.DataFrame()
        df_strava_polyline = pd.DataFrame()

        if self.endpoint_conf['PIPELINE']['STRAVA']:
            df_strava = self.extractStravaData()
            df_strava_clean = self.cleanFitnessData(df_strava)
            df_fitness = df_fitness.append(df_strava_clean)

            # optional extraction for polyline analysis
            #df_strava_clean.to_csv(os.path.join(extract_path, "strava.csv"))
            #df_strava_clean = pd.read_csv(os.path.join(extract_path, "strava.csv"))
            df_strava_polyline = strava.generatePolylineDf(df_strava_clean)

        if self.endpoint_conf['PIPELINE']['WEIGHTLIFTING']:
            df_weightlifting = self.extractWeightliftingData()
            df_weightlifting_clean = self.cleanFitnessData(df_weightlifting)
            df_fitness = df_fitness.append(df_weightlifting_clean)

        if self.endpoint_conf['PIPELINE']['TABLEAU']:
            self.loadFitnessData(df_fitness, 'fitness_anlysis')
            self.loadFitnessData(df_strava_polyline, 'polyline_analysis')
        
        run_time = datetime.combine(date.today(), datetime.now().time()) - datetime.combine(date.today(), self.pipeline_start.time())
        print(f"Pipeline executed, run time: {run_time}")

if __name__ == "__main__":

    pipeline = FitnessHandler()
    pipeline.runPipeline()
