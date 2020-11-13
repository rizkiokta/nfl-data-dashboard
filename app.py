import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from source_data import sqling, figure
import dash_table
from dash.dependencies import Input, Output, State
import sqlite3

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#list of teams
teams = {
    'ARI':'Arizona Cardinals',
    'ATL':'Atlanta Falcons',
    'BAL':'Baltimore Ravens',
    'BUF':'Buffalo Bills',
    'CAR':'Carolina Panthers',
    'CHI':'Chicago Bears',
    'CIN':'Cincinnati Bengals',
    'CLE':'Cleveland Browns',
    'DAL':'Dallas Cowboys',
    'DEN':'Denver Broncos',
    'DET':'Detroit Lions',
    'GB':'Green Bay Packers',
    'HOU':'Houston Texans',
    'IND':'Indianapolis Colts',
    'JAX':'Jacksonville Jaguars',
    'KC':'Kansas City Chiefs',
    'LA':'Los Angeles Rams',
    'LAC':'Los Angeles Chargers',    
    'MIA':'Miami Dolphins',
    'MIN':'Minnesota Vikings',
    'NE':'New England Patriots',
    'NO':'New Orleans Saints',
    'NYG':'New York Giants',
    'NYJ':'New York Jets',
    'OAK':'Oakland Raiders',
    'PHI':'Philadelphia Eagles',
    'PIT':'Pittsburg Steelers',
    'SEA':'Seattle Seahawks',
    'SF':'San Fransisco 49ers',
    'TB':'Tampa Bay Buccaneers',
    'TEN':'Tennesee Titans',
    'WAS':'Washington Redskins',
}
team_options = [{'label' : teams[key], 'value': key} for key in teams.keys()]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# STREAM DATA FROM SQLITE
db = sqlite3.connect("nfl2018.db")
c = db.cursor()
df = sqling.select_data('PLAYS', db)

# THIS SHOULD BE CHANGED TOO
## FIG ON PLOTLY ##
# fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

# OPERATORS
operators = [['ge ', '>='],
['le ', '<='],
['lt ', '<'],
['gt ', '>'],
['ne ', '!='],
['eq ', '='],
['contains '],
['datestartswith ']]

# HTML LAYOUT
#set the page size
PAGE_SIZE = 200
#build the app layout
app.layout = html.Div([
    html.H1("NFL 2018 PASSING PLAYS DATA"),
    html.P(''),
    dcc.Tabs([
        # tab 1 for data displaying and inspection
        dcc.Tab(label='Filter and Sort', children=[  
            html.P('Filter and sort the data.'),
            html.P(''),
            html.Label('Choose a Table'),
            # dropdown for table selection
            dcc.Dropdown(
                id = "table-selection",
                options = [
                    {'label' : 'Plays Data', 'value' : 'PLAYS'},
                    {'label' : 'Players Data', 'value' : 'PLAYERS'},
                    {'label' : 'Games Data', 'value' : 'GAMES'}
                ],
                value='PLAYS'
            ),
            dash_table.DataTable(
                id='table-sorting-filtering',
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto'
            },
            style_table={
                'maxHeight': '800px'
                ,'overflowY': 'scroll'
            },
            columns=[
                {'name': i, 'id': i} for i in df.columns
            ],
            page_current= 0,
            page_size= PAGE_SIZE,
            page_action='custom',
            filter_action='custom',
            filter_query='',
            sort_action='custom',
            sort_mode='multi',
            sort_by=[])
        ]),
        # tab 2 for player tracking data
        dcc.Tab(label='Player Tracking Data', children=[
            html.Div([
                # dropdown for home team selection
                dcc.Dropdown(
                    id='home-team',
                    options=team_options,
                    value='ARI',
                    style={'width':'49%', 'display':'inline-block'},
                    placeholder='Select Home Team'
                ),
                # dropdown for visitor team selection
                dcc.Dropdown(
                    id='visitor-team',
                    style={'width':'49%', 'display':'inline-block'},
                    placeholder='Select Visitor Team',
                    value='WAS'
                ),
                # dropdown for quarter play selection
                dcc.Dropdown(
                    id='quarter-play',
                    options=[{'label': x+1, 'value': x+1} for x in range(0,4)],
                    style={'width':'30%'},
                    placeholder='Select Quarter Play',
                    value=1
                ),
                html.P('Time in Quarter'),
                # slider for time in quarter selection
                dcc.Slider(
                    id='time-in-quarter',
                    step=None,
                ),
                html.P('Animation Type'),
                dcc.Dropdown(
                    id='animation-type',
                    options=[
                        {'label':'Normal', 'value':'N'},
                        {'label':'Field Control', 'value':'V'}
                        ],
                    value='N'
                ),
                html.Hr(),
                html.Div(
                    id='play-information',
                    children = 
                    [
                        html.Div(id='first-line-info', children='callback not executed'),
                        html.Div(id='second-line-info', children='callback not executed'),
                        html.Div(id='third-line-info', children='callback not executed'),
                        html.Div(id='fourth-line-info', children='callback not executed')
                    ]
                ),
                dcc.Graph(
                    id='tracks-animation'
                ),
                # dcc.
            ]),
            html.Hr(),
        ])
    ])
])# end div

# filter part function
def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value
    return [None] * 3

# callback for home team reactive options
@app.callback(
    Output('visitor-team', 'options'),
    [Input('home-team', 'value')]
)

def update_dropdown_visitorTeam(name):
    db = sqlite3.connect("nfl2018.db")
    c = db.cursor()
    visitorTeam_list = sqling.select_visitorTeam(name, db, to_list=True)
    return [{'label' : teams[visitor], 'value' : visitor} for visitor in visitorTeam_list]

# callback for time in quarter reactive selection
@app.callback(
    [Output('time-in-quarter', 'marks'),
    Output('time-in-quarter', 'min'),
    Output('time-in-quarter', 'max')],
    [Input('home-team', 'value'),
    Input('visitor-team', 'value'),
    Input('quarter-play', 'value')]
)

def update_slider(home_team, visitor_team, quarter):
    db = sqlite3.connect("nfl2018.db")
    c = db.cursor()
    gameId = sqling.select_games(home_team, visitor_team, db)['gameId'].values[0]
    df = sqling.select_plays(gameId, quarter, db)[['playId' ,'gameClock']]
    return df.set_index('playId')['gameClock'].to_dict(), df['playId'].values.min(), df['playId'].values.max()

# callback for tracks animation
@app.callback(
    [Output('tracks-animation', 'figure'),
    Output('first-line-info', 'children'),
    Output('second-line-info', 'children'),
    Output('third-line-info', 'children'),
    Output('fourth-line-info', 'children')],
    [Input('home-team', 'value'),
    Input('visitor-team', 'value'),
    Input('quarter-play', 'value'),
    Input('time-in-quarter', 'value')]
)

def update_animation(type, home_team, visitor_team, quarter, time):
    db = sqlite3.connect("nfl2018.db")
    c = db.cursor()
    gameId = sqling.select_games(home_team, visitor_team, db)['gameId'].values[0]
    playId = time
    play = sqling.select_play(gameId, playId, db)
    df = sqling.select_tracks(gameId, playId, db)
    if play.passResult[0] == 'C':
        play_result = 'complete'
    else :
        play_result = 'incomplete'
    if play.playResult[0] > 0:
        result_yard = 'gain of'
    else :
        result_yard = 'loss of'
    first_line = f'{play.down[0]} down & {play.yardsToGo[0]} on {play.yardlineSide[0]}{play.yardlineNumber[0]} {play.possessionTeam[0]} offense in {play.offenseFormation[0]} with {play.personnelO[0]}'
    second_line = f'{home_team}:{play.preSnapHomeScore[0]} {visitor_team}:{play.preSnapVisitorScore[0]}'
    third_line = f'{play.defendersInTheBox[0]} {visitor_team} in the box with {play.personnelD[0]} rushing {play.numberOfPassRushers[0]} in result {play_result} with {result_yard} {play.playResult[0]} yards'
    fourth_line = f'{play.playDescription[0]}'
    play = figure.plotly_animate(df)
    return play, first_line, second_line, third_line, fourth_line

# callback for filtering reactive table
@app.callback(
    [Output('table-sorting-filtering', 'data'),
    Output('table-sorting-filtering', 'columns')],
    [Input('table-sorting-filtering', "page_current"),
    Input('table-sorting-filtering', "page_size"),
    Input('table-sorting-filtering', 'sort_by'),
    Input('table-sorting-filtering', 'filter_query'),
    Input('table-selection', 'value')])

# CHANGING TABLE
# THIS SHOULD BE CHANGE TO DATA
## STREAM ON SQLITE ##

# UPDATING TABLE
def update_table(page_current, page_size, sort_by, filter, table='PLAYS'):
    db = sqlite3.connect("nfl2018.db")
    c = db.cursor()
    df = sqling.select_data(table, db)
    filtering_expressions = filter.split(' && ')
    dff = df

    # FILTER
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    
    # SORT
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False)

    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records'), [{"name": i, "id": i} for i in df.columns]

# MAIN FUN
if __name__ == '__main__':
    app.run_server(debug=True)