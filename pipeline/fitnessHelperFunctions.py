# helper functions

from pandleau import *
import pandas as pd
import datetime
import os, sys

path_to_conf = "./conf/"
path_to_logs = "./logs/"
path_to_tableau = "./tableau/"


def make_uid(row) :
    '''creates workout uid'''
    return str(int(row['Rotation'])) + "." + str(int(row['Workout'])) + "." + str(int(row['Week']))

def make_datetime(r) :
    '''constructs datetime object for each workout'''
    if pd.notnull(r['Date']) :
        datetime_string = datetime.datetime.combine(r['Date'], r['Time'])
        return datetime_string

def make_1rm(x) :
    '''calculates a theoretical 1RM for each lift'''
    if pd.notnull(x) :
        r, w = x.split('x')[0], x.split('x')[1]
        return float(w)*(1 + int(r)/30)
    return None 