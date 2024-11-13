#services/formulaone.py
import requests
import xml.etree.ElementTree as ET
import pandas as pd

#https://documenter.getpostman.com/view/11586746/SztEa7bL#intro
def get_drivers_data():
    url = 'http://ergast.com/api/f1/current/driverStandings.json'
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    df = pd.json_normalize(standings)
    return df

def get_constructors_data():
    url = 'http://ergast.com/api/f1/current/constructorStandings.json'
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    df = pd.json_normalize(standings)
    return df

def get_race_data():
    url = 'http://ergast.com/api/f1/current.json'
    response = requests.get(url)
    data = response.json()
    races = data['MRData']['RaceTable']['Races']
    df = pd.json_normalize(races)
    return df