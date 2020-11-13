import sqlite3
import pandas as pd

def select_data(table, db):
    df = pd.read_sql("SELECT * FROM {}".format(table), db)
    return df

def select_plays(gameId, quarter, db):
    df = pd.read_sql(f"SELECT * FROM PLAYS WHERE (PLAYS.gameId = {gameId} AND PLAYS.gameClock IS NOT NULL AND PLAYS.quarter = {quarter})", db)
    return df

def select_play(gameId, playId, db):
    df = pd.read_sql(f"SELECT * FROM PLAYS WHERE (PLAYS.gameId = {gameId} AND PLAYS.playId = {playId})", db)
    return df

def select_games(homeTeam, visitorTeam, db):
    df = pd.read_sql(f"SELECT * FROM GAMES WHERE (GAMES.homeTeamAbbr = '{homeTeam}' AND GAMES.visitorTeamAbbr = '{visitorTeam}')", db)
    return df

def select_visitorTeam(homeTeamAbbr, db, to_list=False):
    df = pd.read_sql(f"SELECT * FROM GAMES WHERE homeTeamAbbr = '{homeTeamAbbr}'", db)
    if to_list:
        return df['visitorTeamAbbr'].to_list()
    return df['visitorTeamAbbr']

def select_tracks(gameId, playId, db):
    df = pd.read_sql(f"SELECT * FROM TRACKS WHERE (TRACKS.gameId = {gameId} AND TRACKS.playId = {playId})", db)
    return df

def create_teams_tables(db):
    df = pd.read_sql('SELECT * FROM PLAYS', db)
    teams = df.possessionTeam.sort_values().unique()
    
    ### OFFENSE ###
    ## WHOLE LEAGUE VIS ##
    # BAR CHART
    sumPassingPlays = df.sort_values(by='possessionTeam').groupby(by='possessionTeam').size()
    # BAR CHART
    sumOffensePlayResult = df.sort_values(by='possessionTeam').groupby(by='possessionTeam')['offensePlayResult'].sum()
    # BAR CHART
    sumPlayResult = df.sort_values(by='possessionTeam').groupby(by='possessionTeam')['playResult'].sum()
    # STACKED BAR
    sumPassResult = df.sort_values(by='possessionTeam').groupby(by=['possessionTeam', 'passResult']).size().unstack()
    # STACKED BAR
    sumTypeDropback = df.sort_values(by='possessionTeam').groupby(by=['possessionTeam', 'typeDropback']).size().unstack()
    # STACKED BAR
    sumTypeDropbackPlayResult = df.sort_values(by='possessionTeam').groupby(by=['possessionTeam', 'typeDropback'])['playResult'].sum().unstack()

    ## DETAILED VIS ##
    sumDown = df.sort_values(by='possessionTeam').groupby(by=['possessionTeam', 'down']).size().unstack()
    avgDownYardsToGo = df.sort_values(by='possessionTeam').groupby(by=['possessionTeam', 'down'])['yardsToGo'].mean().unstack()
    print(avgDownYardsToGo)


db = sqlite3.connect(r"C:\Users\mrizk\Documents\LEARN\nfl-data-dashboard\nfl-data-dashboard\nfl2018.db")
c = db.cursor()
create_teams_tables(db)
        