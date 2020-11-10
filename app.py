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
                )
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