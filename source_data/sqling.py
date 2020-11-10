import sqlite3
import pandas as pd

def select_data(table, db):
    df = pd.read_sql("SELECT * FROM {}".format(table), db)
    return df

def select_plays(gameId, quarter, db):
    df = pd.read_sql(f"SELECT * FROM PLAYS WHERE (PLAYS.gameId = {gameId} AND PLAYS.gameClock IS NOT NULL AND PLAYS.quarter = {quarter})", db)
    return df

def select_games(homeTeam, visitorTeam, db):
    df = pd.read_sql(f"SELECT * FROM GAMES WHERE (GAMES.homeTeamAbbr = '{homeTeam}' AND GAMES.visitorTeamAbbr = '{visitorTeam}')", db)
    return df

def select_visitorTeam(homeTeamAbbr, db, to_list=False):
    df = pd.read_sql(f"SELECT * FROM GAMES WHERE homeTeamAbbr = '{homeTeamAbbr}'", db)
    if to_list:
        return df['visitorTeamAbbr'].to_list()
    return df['visitorTeamAbbr']