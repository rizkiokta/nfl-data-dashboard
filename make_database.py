import sqlite3
import pandas as pd
import os

conn = sqlite3.connect("nfl2018.db")

c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS GAMES(
    gameId INTEGER PRIMARY KEY UNIQUE NOT NULL,
    gameDate DATE,
    gameTimeEastern TIME,
    homeTeamAbbr TEXT,
    visitorTeamAbbr TEXT,
    week INTEGER
    INDEX gamesIdentifier(gameId)
)''')

c.execute('''
CREATE TABLE IF NOT EXISTS PLAYERS(
    nflId INTEGER PRIMARY KEY UNIQUE NOT NULL,
    height TEXT,
    weight INTEGER,
    birthDate DATE,
    collegeName TEXT,
    position TEXT,
    displayName TEXT
    INDEX playersIdentifier(nflId)
)''')

c.execute('''
CREATE TABLE IF NOT EXISTS PLAYS(
    gameId INTEGER NOT NULL,
    playId INTEGER,
    playDescription TEXT,
    quarter NUMERIC,
    down NUMERIC,
    yardsToGo NUMERIC,
    possessionTeam TEXT,
    playType TEXT,
    yardlineSide TEXT,
    yardlineNumber NUMBER,
    offenseNumber INTEGER,
    offenseFormation TEXT,
    personnelO TEXT,
    defendersInTheBox INTEGER,
    numberOfPassRushers INTEGER,
    personneld TEXT,
    typeDropback TEXT,
    preSnapVisitorScore INTEGER,
    preSnapHomeScore INTEGER,
    gameClock TIME,
    absoluteYardlineNumber INTEGER,
    penaltyCodes TEXT,
    penaltyJerseyNumber TEXT,
    passResult TEXT,
    offensePlayResult INTEGER,
    epa FLOAT,
    isDefensivePI BOOL,
    FOREIGN KEY (gameId) REFERENCES GAMES(gameId)
    INDEX playsIdentifier(gameId, playId)
)''')

c.execute('''
CREATE TABLE IF NOT EXISTS TRACKS(
    time DATETIME,
    x FLOAT,
    y FLOAT,
    s FLOAT,
    a FLOAT,
    dis FLOAT,
    o FLOAT,
    dir FLOAT,
    event TEXT,
    nflId INTEGER,
    displayName TEXT,
    jerseyNumber INTEGER,
    position TEXT,
    team TEXT,
    frameId INTEGER,
    gameId INTEGER,
    playId INTEGER,
    playDirection TEXT,
    route TEXT,
    FOREIGN KEY (nflId) REFERENCES PLAYERS(nflId),
    FOREIGN KEY (gameId) REFERENCES GAMES(gameId),
    FOREIGN KEY (playId) REFERENCES PLAYS(playId)
    INDEX playsIdentifier(gameId, playId, nflId, frameId)
)''')

conn.commit()

files_l = os.listdir("data_feather")

games_path = r"data_feather/games.feather"
plays_path = r"data_feather/plays.feather"
players_path = r"data_feather/players.feather"
tracks_path = ["data_feather/"+f for f in files_l if "week" in f]

def read_and_sql(path, table, con=conn, mode="replace"):
    file = pd.read_feather(path)
    file.to_sql(table, con, if_exists=mode, index=False)

def sqling():
    read_and_sql(games_path, "GAMES")
    read_and_sql(plays_path, "PLAYS")
    read_and_sql(players_path, "PLAYERS")
    for track in tracks_path:
        read_and_sql(track, "TRACKS", mode="append")

sqling()