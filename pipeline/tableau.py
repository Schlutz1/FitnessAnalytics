# Simple wrapper for tableau function
import pandas as pd
import datetime
import sys
import os

# globals
abs_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(abs_path, "..", "log")
tableau_path = os.path.join(abs_path, "..", "extracts")


def makeConversion(df, file_name):
    """convert dataframe to .hyper extract"""

    if not os.path.isdir(tableau_path):
        os.mkdir(tableau_path)

    # make conversion
    if df.shape[1] > 0:

        # overwrite with new file
        file_out = os.path.join(tableau_path, f"{file_name}.xlsx")
        if os.path.isfile(file_out):
            os.remove(file_out)
        df.to_excel(file_out)

def cleanLogs():
    """clean log files function"""

    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    files_logs = [
        f for f in os.listdir("./")
        if os.path.isfile(os.path.join("./", f)) and ".log" in f
        or "hyper_db_" in f
    ]

    for file in files_logs:
        os.rename(file, os.path.join(log_path, file))

    print("Directory cleaned")
