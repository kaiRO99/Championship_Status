#views.py
from django.shortcuts import render
from django.utils.safestring import mark_safe
from .services.formulaone_service import get_drivers_data, get_constructors_data, get_race_data
from .services.football_service import get_league_table_data
import pandas as pd
from .models import driver_collection, constructor_collection, race_collection, remaining_points_collection, premier_league_collection, laliga_collection
from datetime import datetime, timedelta
import numpy as np
import pytz
# Create your views here.
def home(request):
    return render(request, "base.html")

def premier_league(request):
    total_matches = 38
    mongo_data = premier_league_collection.find_one({'Position': 1})
    if not needs_update(mongo_data['created_at']):
        premier_league_table_data = get_db_premier_league_data()
        premier_league_table_data = premier_league_table_data.sort_values(by='Position', ascending=True)
        html_table = mark_safe(premier_league_table_data.to_html(index=False,escape=False))
    else:
        premier_league_table_data = get_league_table_data('PL')
        premier_league_table_data['Matches Remaining'] = total_matches - premier_league_table_data['playedGames'].astype(int)
        premier_league_table_data['Points Available'] = premier_league_table_data['Matches Remaining']*3
        premier_league_table_data['points'] = premier_league_table_data['points'].astype(int)
        premier_league_table_data['Delta'] = premier_league_table_data.iloc[0]['points'] - premier_league_table_data['points']
        premier_league_table_data['team.crest'] = premier_league_table_data['team.crest'].apply(lambda url: f'<img src="{url}" height="40"/>')
        premier_league_table_data.rename(columns={'position':'Position','team.crest':'',
                                                'playedGames':'Matches Played',
                                                'points':'Points', 'team.name':'Team'}, inplace=True )
        premier_league_table_data['Status'] = np.where(
                (premier_league_table_data['Delta']<premier_league_table_data['Points Available']),
                'In','Out')
        #? what if points tied
        premier_league_table_data = premier_league_table_data[['Position','','Team',
                                                            'Points','Matches Played',
                                                            'Matches Remaining','Points Available',
                                                            'Delta','Status']]
        premier_league_table_data = premier_league_table_data.sort_values(by='Position', ascending=True)
        #convert to html table to display images
        html_table = mark_safe(premier_league_table_data.to_html(index=False,escape=False))
        add_premier_league(premier_league_table_data)
    return render(request, "premier_league.html",{'html_table':html_table})

def laliga(request):
    total_matches = 38
    #!check if db empty?
    mongo_data = laliga_collection.find_one({'Position': 1})
    if not needs_update(mongo_data['created_at']):
        laliga_table_data = get_db_laliga_data()
        laliga_table_data = laliga_table_data.sort_values(by='Position', ascending=True)
        html_table = mark_safe(laliga_table_data.to_html(index=False,escape=False))
    else:
        laliga_table_data = get_league_table_data('PD')
        laliga_table_data['Matches Remaining'] = total_matches - laliga_table_data['playedGames'].astype(int)
        laliga_table_data['Points Available'] = laliga_table_data['Matches Remaining']*3
        laliga_table_data['points'] = laliga_table_data['points'].astype(int)
        laliga_table_data['Delta'] = laliga_table_data.iloc[0]['points'] - laliga_table_data['points']
        laliga_table_data['team.crest'] = laliga_table_data['team.crest'].apply(lambda url: f'<img src="{url}" height="40"/>')
        laliga_table_data.rename(columns={'position':'Position','team.crest':'',
                                                'playedGames':'Matches Played',
                                                'points':'Points', 'team.name':'Team'}, inplace=True )
        laliga_table_data['Status'] = np.where(
                (laliga_table_data['Delta']<laliga_table_data['Points Available']),
                'In','Out')
        #? what if points tied
        laliga_table_data = laliga_table_data[['Position','','Team',
                                                            'Points','Matches Played',
                                                            'Matches Remaining','Points Available',
                                                            'Delta','Status']]
        laliga_table_data = laliga_table_data.sort_values(by='Position', ascending=True)
        #convert to html table to display images
        html_table = mark_safe(laliga_table_data.to_html(index=False,escape=False))
        add_laliga(laliga_table_data)
    return render(request, "laliga.html",{'html_table':html_table})

def f1(request):
    #check if data stale 
    mongo_data = premier_league_collection.find_one({'Position': 1})
    if not needs_update(mongo_data['created_at']):
        drivers_champ_data = get_db_driver_data()
        constructors_champ_data = get_db_constructors_data()
        race_data = get_db_race_data()
        remaining_points = get_db_remaining_points()
    else:
        #* get drivers data
        drivers_champ_data = get_drivers_data()
        drivers_champ_data['Name'] = drivers_champ_data['Driver.givenName'] +" "+drivers_champ_data['Driver.familyName']
        drivers_champ_data.rename(columns={'position':'Position',
                                            'wins':'Wins',
                                            'points':'Points'}, inplace=True )
        drivers_champ_data['Points'] = drivers_champ_data['Points'].astype(int)
        drivers_champ_data['Position'] = drivers_champ_data['Position'].astype(int)
        drivers_champ_data['Delta'] = drivers_champ_data.iloc[0]['Points'] - drivers_champ_data['Points']
        drivers_champ_data = drivers_champ_data[['Position', 'Name', 'Wins', 'Points','Delta']]
        
        #* get constructors data
        constructors_champ_data = get_constructors_data()
        constructors_champ_data.rename(columns={'position':'Position', 'wins':'Wins',
                                                'points':'Points','Constructor.name':'Name'}, inplace=True )
        constructors_champ_data['Points'] = constructors_champ_data['Points'].astype(int)
        constructors_champ_data['Position'] = constructors_champ_data['Position'].astype(int)
        constructors_champ_data['Delta'] = constructors_champ_data.iloc[0]['Points'] - constructors_champ_data['Points']
        drivers_champ_data = drivers_champ_data[['Position', 'Name', 'Wins', 'Points','Delta']]
        
        #* race data
        race_data = get_race_data()
        race_data['date'] = race_data['date']+' '+race_data['time']
        race_data['date'] = pd.to_datetime(race_data['date'], format = "mixed") #convert to datetime object
        race_data['date'] = race_data['date'].dt.tz_convert('America/Toronto')
        totonto_tz = datetime.now(pytz.timezone('America/Toronto'))
        race_data = race_data[race_data['date'] > totonto_tz]
        race_data['date'] = race_data['date'].dt.tz_localize(None)
        race_data['Drivers Points Available'] = np.where(pd.isna(race_data['Sprint.date']), 26, 34)
        race_data['Constructors Points Available'] = np.where(pd.isna(race_data['Sprint.date']),44,59)
        race_data.rename(columns={'round':'Round',
                                'raceName':'Name',
                                'date':'Date'}, inplace=True )
        race_data['Round'] = race_data['Round'].astype(int)
        race_data = race_data[['Round', 'Name', 'Date', 'Drivers Points Available','Constructors Points Available']]

        #*points remaining
        remaining_points = pd.DataFrame()
        remaining_points.loc[0,'Drivers'] = race_data['Drivers Points Available'].sum()
        remaining_points.loc[0,'Constructors'] = race_data['Constructors Points Available'].sum()
        remaining_points['Drivers'] = (remaining_points['Drivers']).astype(int)
        remaining_points['Constructors'] = (remaining_points['Constructors']).astype(int)
        
        #* add status column
        drivers_available_points = remaining_points['Drivers'].iloc[0]
        drivers_champ_data['Wins'] = drivers_champ_data['Wins'].astype(int)
        drivers_champ_data['Status'] = np.where(
            ((drivers_champ_data['Delta']<drivers_available_points)|
            ((drivers_champ_data['Delta']==drivers_available_points)&
            (len(race_data)>(abs(drivers_champ_data.iloc[0]['Wins']-drivers_champ_data['Wins'])))
            )),
            'In','Out')
        constructors_available_points = remaining_points['Constructors'].iloc[0]
        constructors_champ_data['Wins'] = constructors_champ_data['Wins'].astype(int)
        constructors_champ_data['Status'] = np.where(
            ((constructors_champ_data['Delta']<constructors_available_points)|
            ((constructors_champ_data['Delta']==constructors_available_points)&
            (len(race_data)>(abs(constructors_champ_data.iloc[0]['Wins']-constructors_champ_data['Wins'])))
            )),
            'In','Out')
        
        #*add to db
        add_drivers(drivers_champ_data)
        if 'created_at' in drivers_champ_data.columns:
            drivers_champ_data.drop('created_at', axis=1, inplace=True)
        add_constructors(constructors_champ_data)
        add_races(race_data) 
        add_remaining_points(remaining_points) 
    
    drivers_champ_data = drivers_champ_data.sort_values(by='Position', ascending=True)
    constructors_champ_data = constructors_champ_data.sort_values(by='Position', ascending=True)
    race_data = race_data.sort_values(by='Round', ascending=True)   
     
    return render(request, "f1.html",
                  {'drivers_champ_data':drivers_champ_data.to_dict('records'),
                   'constructors_champ_data':constructors_champ_data.to_dict('records'),
                   'race_data':race_data.to_dict('records'),
                   'remaining_points_data':remaining_points.to_dict('records')})

#*check if update required 
def needs_update(last_updated):    
    now = datetime.now()
    weekday = now.weekday()
    time = now.time()
    six_pm = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0).time()
    saturday_6pm = (now - timedelta(days=(now.weekday() + 2) % 7)).replace(hour=18, minute=0, second=0, microsecond=0)
    sunday_6pm = (now - timedelta(days=(now.weekday() + 1) % 7)).replace(hour=18, minute=0, second=0, microsecond=0)
    if ((weekday == 5 or weekday == 6) and time >= six_pm) and \
   (last_updated < saturday_6pm or last_updated < sunday_6pm):
        return True
    return False

#* Calculate if winning is possible, f1 only
def can_win(df,remaining_points,race_data, column):
    available_points = remaining_points[column].iloc[0]
    if ((df['Delta']<available_points)or
        ((df['Delta']==available_points)and
         (len(race_data)>(abs(df.iloc[0]['Wins']-df['Wins'])))
         )
        ):
        return True
    else:
        return False
    
#* Add data to MongoDB
def add_premier_league(table):
    table['created_at'] = datetime.now()
    premier_league_collection.delete_many({})
    premier_league_collection.insert_many(table.to_dict('records'))
    
def add_laliga(table):
    table['created_at'] = datetime.now()
    laliga_collection.delete_many({})
    laliga_collection.insert_many(table.to_dict('records'))

def add_drivers(drivers):
    drivers['created_at'] = datetime.now()
    driver_collection.delete_many({})
    driver_collection.insert_many(drivers.to_dict('records'))

def add_constructors(constructors):
    constructor_collection.delete_many({})
    constructor_collection.insert_many(constructors.to_dict('records'))
    
def add_races(races):
    race_collection.delete_many({})
    race_collection.insert_many(races.to_dict('records'))
    
def add_remaining_points(remaining_points):
    remaining_points_collection.delete_many({})
    remaining_points_collection.insert_many(remaining_points.to_dict('records'))

#* get data from MongoDB
def get_db_premier_league_data():
    premier_league_table_data = pd.DataFrame(premier_league_collection.find({}))
    if '_id' in premier_league_table_data.columns:
        premier_league_table_data.drop('_id', axis=1, inplace=True)
    if 'created_at' in premier_league_table_data.columns:
        premier_league_table_data.drop('created_at', axis=1, inplace=True)
    return premier_league_table_data

def get_db_laliga_data():
    laliga_table_data = pd.DataFrame(laliga_collection.find({}))
    if '_id' in laliga_table_data.columns:
        laliga_table_data.drop('_id', axis=1, inplace=True)
    if 'created_at' in laliga_table_data.columns:
        laliga_table_data.drop('created_at', axis=1, inplace=True)
    return laliga_table_data

def get_db_driver_data():
    drivers_champ_data = pd.DataFrame(driver_collection.find({}))
    if '_id' in drivers_champ_data.columns:
        drivers_champ_data.drop('_id', axis=1, inplace=True)
    if 'created_at' in drivers_champ_data.columns:
        drivers_champ_data.drop('created_at', axis=1, inplace=True)
    return drivers_champ_data

def get_db_constructors_data():
    constructors_champ_data = pd.DataFrame(constructor_collection.find({}))
    if '_id' in constructors_champ_data.columns:
        constructors_champ_data.drop('_id', axis=1, inplace=True)
    return constructors_champ_data

def get_db_race_data():
    race_data = pd.DataFrame(race_collection.find({}))
    if '_id' in race_data.columns:
        race_data.drop('_id', axis=1, inplace=True)
    return race_data
    
def get_db_remaining_points():
    remaining_points_data = pd.DataFrame(remaining_points_collection.find({}))
    if '_id' in remaining_points_data.columns:
        remaining_points_data.drop('_id', axis=1, inplace=True)
    return remaining_points_data