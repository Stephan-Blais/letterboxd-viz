import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

app = dash.Dash(__name__)

month_dict = {1: 'January', 2: 'February', 3:'March',
4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',
10:'October',11:'November',12:'December'}
# Dataframes have numbers for month, converting to actual month names

df = pd.read_csv('https://raw.githubusercontent.com/Stephan-Blais/letterboxd-viz/main/TMDB%20w%20Binary%20Genre.csv')
df['Release Month'].replace(month_dict, inplace =True)
# Using df with non-duplicated rows for "Total Count of All Films" view

df_dupes = pd.read_csv("https://raw.githubusercontent.com/Stephan-Blais/letterboxd-viz/main/TMDB%20w%20Dupes.csv")
df_dupes['Release Month'].replace(month_dict, inplace =True)
# Using this for other chart versions

df_genre_listed = pd.read_csv("https://raw.githubusercontent.com/Stephan-Blais/letterboxd-viz/main/TMDB%20w%20Genre%20%23%20Cols.csv")
df_genre_listed = df_genre_listed.drop(columns = ['Unnamed: 0', 'ID', 'Release Year', 'Release Month', 'Release Day', 'Poster Path'])
df_genre_listed['Release Date'] = pd.to_datetime(df_genre_listed['Release Date']).dt.date
# Using this for datatable

# ------------------------------------------------------------------------------
# App layout

app.layout = html.Div([

    html.Center(
        html.A([
            html.Img(src = 'https://raw.githubusercontent.com/Stephan-Blais/letterboxd-viz/main/Assets/lb_dashboard_no_background.jpg',
                    width = 640,
                    height = 360,
                    )
        ],
            href = 'https://letterboxd.com/stephanblais/',
            target = '_blank',
            rel = 'noreferrer noopener',   
        ),
    ),

    html.Center(
        html.I(
            children = '(Refresh page to quickly reset selections below to default)'
        ),
    ),

    html.Br(),

    html.Center(
    dcc.Checklist(
        id = 'checklist',

        options = [{'label':str(g),'value':g} for g in sorted(df_dupes['Genre'].unique())],
        value = [],
        labelStyle={'display': 'inline-block'},
    )
    ),

    html.Br(),

    dcc.Dropdown(
        id = 'dropdown',
        options = [
            {'label': 'Release Year', 'value': 'Release Year'},
            {'label': 'Release Month', 'value': 'Release Month'},
            {'label': 'Release Day', 'value': 'Release Day'},],
        value = 'Release Year',
        clearable = False,
    ),

    html.Br(),
    html.Br(),

    html.Center(
        html.H3(id = 'barchart-title', children = [''])
    ),
    
    dcc.Graph(
        id='my-chart',
        figure = {},
    ),

    html.Center(
        html.H3(id = 'table-title', children = [''])
    ),
    

    dash_table.DataTable(
        id='my-table',
        columns=[{"name": i, "id": i} for i in df_genre_listed.columns],
        data = [],
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        page_size = 12,
    )
])

# ------------------------------------------------------------------------------
# Callback
@app.callback(
    [Output(component_id = 'barchart-title', component_property = 'children'),
    Output(component_id='my-chart', component_property='figure'),
    Output(component_id = 'table-title', component_property = 'children'),
    Output(component_id = 'my-table', component_property= 'data')],
    [Input(component_id = 'checklist', component_property='value'),
    Input(component_id = 'dropdown', component_property = 'value')]
)

def update_my_graph(genre_chosen,interval_chosen):

    df_sub = df_dupes.groupby(['Genre', interval_chosen]).size().reset_index(name = 'Count_of_Films')
    df_sub['Genre_Filter'] = df_sub['Genre']
    df_sub = df_sub[(df_sub['Genre_Filter'].isin(genre_chosen))]
    
    dff = df.groupby([interval_chosen]).size().reset_index(name ='Count of All Films')

    df_table_filtered = df_genre_listed[(df_genre_listed['Genre 1'].isin(genre_chosen)|df_genre_listed['Genre 2'].isin(genre_chosen)|
    df_genre_listed['Genre 3'].isin(genre_chosen)|df_genre_listed['Genre 4'].isin(genre_chosen)|
    df_genre_listed['Genre 5'].isin(genre_chosen)|df_genre_listed['Genre 6'].isin(genre_chosen)|
    df_genre_listed['Genre 7'].isin(genre_chosen))]

    df_table = df_genre_listed.copy()
    

    if len(genre_chosen) == 1:
        fig = px.bar(df_sub,
                            x = df_sub[interval_chosen],
                            y = df_sub['Count_of_Films'],
                            labels = dict(Count_of_Films = f'Count of {genre_chosen[0]} Films'),
                            color= df_sub['Genre']
        )

        fig.update_traces(hovertemplate = 'Year: %{label}<br>Films: %{value}'),

        if interval_chosen == 'Release Month':
            fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray': list(month_dict.values())})
            fig.update_traces(hovertemplate = 'Month: %{label}<br>Films: %{value}')

        if interval_chosen == 'Release Day':
            fig.update_traces(hovertemplate = 'Day of Month: %{label}<br>Films: %{value}')

        barchart_title =  f'Count of {genre_chosen[0]} Films By '+ f'{interval_chosen}'

        table = df_table_filtered.to_dict('records')

        table_title = f'List of {genre_chosen[0]} Films'

        return barchart_title, fig, table_title, table 
        
    
    elif len(genre_chosen) > 1:
        fig = px.bar(df_sub,
                            title= '<b>Note:</b> Films can have more than 1 genre' + 
                            '<br>When selecting more than 1 genre, the chart shifts to represent the '+
                            '<i>Count of Selected Genres</i>,' +
                            '<br>rather than the <i>Absolute Number of Films</i>',
                            x = df_sub[interval_chosen],
                            y = df_sub['Count_of_Films'],
                            labels = dict(Count_of_Films = 'Count of Films in Selected Genres'),
                            color= df_sub['Genre']
            )

        fig.update_traces(hovertemplate = 'Year: %{label}<br>Films: %{value}'),

        if interval_chosen == 'Release Month':
            fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray': list(month_dict.values())})
            fig.update_traces(hovertemplate = 'Month: %{label}<br>Films: %{value}')

        if interval_chosen == 'Release Day':
            fig.update_traces(hovertemplate = 'Day of Month: %{label}<br>Films: %{value}')

        barchart_title = 'Count of Selected Genres By ' + f'{interval_chosen}'

        table = df_table_filtered.to_dict('records')

        table_title = 'List of Films in Selected Genres'

        return barchart_title, fig, table_title, table 
    
    else:
        fig = px.bar(dff, 
                                    x = dff[interval_chosen],
                                    y = dff['Count of All Films'],
        )
        fig.update_traces(hovertemplate = 'Year: %{label}<br>Films: %{value}'),

        if interval_chosen == 'Release Month':
            fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray': list(month_dict.values())})
            fig.update_traces(hovertemplate = 'Month: %{label}<br>Films: %{value}')

        if interval_chosen == 'Release Day':
            fig.update_traces(hovertemplate = 'Day of Month: %{label}<br>Films: %{value}')
        
        barchart_title = 'Count of All Films By ' + f'{interval_chosen}'

        table = df_table.to_dict('records') 

        table_title = 'List of All Films'

        return barchart_title, fig, table_title, table 


if __name__ == '__main__':
    app.run_server(debug=True)

