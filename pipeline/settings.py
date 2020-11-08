# settings.py
from dotenv import load_dotenv
import os

def getEnv():
    ''' loads env variables '''
    dotenv_path = os.path.join('..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    