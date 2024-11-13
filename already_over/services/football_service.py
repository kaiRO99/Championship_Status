#services/formulaone.py
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from dotenv import load_dotenv
import os
import datetime

#https://www.football-data.org/documentation/quickstart

def get_league_table_data(id):
    """

    """
    today = datetime.date.today()
    year = str(today.year)
    load_dotenv()
    url = 'https://api.football-data.org/v4/competitions/'+id+'/standings?season='+year
    headers = {'X-Auth-Token': os.getenv('FOOTBALL_KEY')}
    response = requests.get(url, headers = headers)
    data = response.json()
    table = data['standings'][0]['table']
    df = pd.json_normalize(table)
    return df
    
def get_team_data():

    load_dotenv()
    url = 'http://ergast.com/api/f1/current/constructorStandings.json'
    headers = {'X-Auth-Token': os.getenv('FOOTBALL_KEY')}
    response = requests.get(url, headers = headers)
    data = response.json()
    #year: data['MRData']['StandingsTable']['season']
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    # print(standings[0])
    df = pd.json_normalize(standings)
   
    return df
