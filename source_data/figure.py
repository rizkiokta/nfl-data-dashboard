# https://www.kaggle.com/robikscube/nfl-big-data-bowl-plotting-player-position
# Utility Libraries
import plotly_express as px
import plotly.graph_objects as go

def plotly_animate(df):
    fig = px.scatter(
        df,
        x = 'x', y = 'y',
        color='team',
        text='position',
        animation_frame='time',
        # animation_group='position',
        range_x=[0, 120], range_y=[0, 60],
        hover_data=['displayName', 'jerseyNumber', 's', 'a', 'dis', 'o', 'playDirection']
    )
    fig.update_traces(textposition='top center', marker_size=10)
    fig.update_layout(paper_bgcolor='darkgreen', plot_bgcolor='darkgreen', font_color='white')
    return fig