import pandas as pd
import numpy as np
import datetime, re
from datetime import datetime, time
import matplotlib as mpl
from matplotlib.colors import ListedColormap
import plotly.express as px
import math
import dash
from dash import html, dcc, dash_table, Dash, Output, Input, callback

# Create a dataframe which includes Call Types, Units, Call Locations, Call Date and Time,
# and includes latitude and longitude with the associated incident addresses.
# The CSV file was created in Jupyter Labs from First Due Software utilized by the
# Danbury Fire Department. The calls were imported from First Due starting in April 2023 up to 
# the end of the year 2023. The software was first implemented in the Spring of 2023.
# The Data was extracted, transformed, and built into a dataframe using the Pandas library,
# and was then saved into a CSV file for use in this application. This application will show 
# various data points regarding those responses including total number of calls, call density in 
# throughout the City of Danbury, and distribution of those calls.

df = pd.read_csv('2023_incident_dataframe.csv',index_col=0)

time = [df.Call_Date_Time.iloc[x][-5:] for x in range(len(df))]
date = [df.Call_Date_Time.iloc[x][:-6] for x in range(len(df))]

time = pd.DataFrame({'Date':date,'Time':time})
df = pd.concat([df,time],axis=1, ignore_index=True,)
cols = ['Latitude','Longitude','Call_Location','Units','Call_Type','Call_Date_Time','Date','Time']

df.rename(columns={x:y for x,y in zip(df.columns.tolist(),cols)},inplace=True)
df.drop(columns='Call_Date_Time',inplace=True)

# Develop a color map to help with the visualizations. 
# Such as assigning a color spectrum for call types on frequently visited addresses.

def graph_colors(df_graph_category,len_df_category,color='red'):
    
    red = px.colors.n_colors('rgb(255,0,0)','rgb(.001,0,255)',len_df_category,colortype='rgb')
    blue = px.colors.n_colors('rgb(0,0,255)','rgb(255,0,.001)',len_df_category,colortype='rgb')
    green = px.colors.n_colors('rgb(0,255,0)','rgb(0,.001,255)',len_df_category,colortype='rgb')
    yellow = px.colors.n_colors('rgb(255,255,0)','rgb(.001,0,255)',len_df_category,colortype='rgb')
    
    color_list = {'red':red,'blue':blue,'green':green,'yellow':yellow}
    
    mapper = {x:y for x,y in zip(df_graph_category,color_list[color])}
    
    return mapper
# Define functions that will call up Company level incident information and incident location density.

companies = ['ALL','TAC1','SQ21','E22','E23','E24','E25','E26','T1','C30']

times = [f'0{x}:00' if x < 10 else f'{x}:00' for x in range(24)]
times.append('23:59')

months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

# Calls by company's
def calls_by_company(company,df=df):
    company = company.upper()
    if company=='ALL':
        bar = px.histogram(df,
                           x='Call_Type',
                           color='Call_Type',
                           color_discrete_sequence=px.colors.sequential.thermal,
                           title="DFD Incident Count by Type",
                           height=800,
                           width=1800)
        bar.update_layout(yaxis_title='Number of Incidents',
                          xaxis_title='Call Type',
                          showlegend=False)
        bar.update_xaxes(tickangle=45,
                         tickfont=dict(size=10))
        return bar
    else:
        calls = df[df.Units.str.contains(company)]
        bar = px.histogram(calls,
                           x='Call_Type',
                           color='Call_Type',
                           color_discrete_map=graph_colors(calls.Call_Type.unique().tolist(),
                                                                len(calls.Call_Type.unique().tolist()),
                                                                color='red'),
                           title=f"{company} Incident Count by Type",
                           height=800,
                           width=1800)
        bar.update_layout(yaxis_title='Number of Incidents',
                          xaxis_title='Call Type',
                          showlegend=False)
        bar.update_xaxes(tickangle=45,
                         tickfont=dict(size=10))
        return bar

# heatmap showing incident occurence density
def company_heatmap(company, df=df):
    company = company.upper()
    
    # Lat/Long of each station to center the map for a companies primary response district
    district = {'HQ':(41.393510,-73.455480),
                'E23':(41.407951,-73.436729),
                'E24':(41.413050,-73.422240),
                'E25':(41.427157,-73.504407),
                'E26':(41.373615,-73.487025)}
    
    if company not in ['E23','E24','E25','E26']:
        lat = district['HQ'][0]
        long = district['HQ'][1]
    else:
        lat=district[company][0]
        long=district[company][1]
    
    if company=='ALL':
        fig = px.density_mapbox(df,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Call_Type','Call_Location'],
                                center={'lat':lat,'lon':long},
                                zoom=11,
                                mapbox_style='open-street-map',
                                radius=6,
                                title= "Danbury Fire Department Incident Concentration Heatmap",
                                height=800,
                                width=800,
                               )
        return fig
    else:
        company_df = df[df.Units.str.contains(company)]
        fig = px.density_mapbox(company_df,
                            lat='Latitude',
                            lon='Longitude',
                            hover_data=['Call_Type','Call_Location'],
                            center={'lat':lat,'lon':long},
                            zoom=12,
                            mapbox_style='open-street-map',
                            radius=6,
                            title= f'Danbury Fire Department Incident Concentration Heatmap for {company.upper()}',
                            height=800,
                            width=800,
                           )
        return fig  

def hourly_incident_volume(company,df=df):
    hrly_vol_df = pd.DataFrame({'Times':[times[t]+'-'+times[t+1] for t in range(24)]})

    for comp in companies:
        count =[]
        for t in range(24):
            if comp == 'ALL':
                total_count = df[(df.Time>times[t]) & (df.Time<times[t+1])].Call_Type.count()
                count.append(total_count)
            else:
                comp_count = df[(df.Units==comp) & (df.Time>times[t]) & (df.Time<times[t+1])].Call_Type.count()
                count.append(comp_count)

        hrly_vol_df = pd.concat([hrly_vol_df,pd.DataFrame({comp:count})],axis=1,ignore_index=True)
    
    columns = ['Time_Period']
    [columns.append(c) for c in companies]
    column_map = {x:y for x,y in zip(hrly_vol_df.columns,columns)}
    hrly_vol_df.rename(columns=column_map, inplace=True)
    
    fig = px.bar(hrly_vol_df,
                 x='Time_Period',
                 y=company,
                 color='Time_Period',
                 color_discrete_map=graph_colors(hrly_vol_df.Time_Period,
                                                 len(hrly_vol_df),
                                                 color='blue'),
                 title=f"Incident Volume by Hour Throughout the Day: {company}",
                 width=1000,
                 height=800)
    fig.update_layout(showlegend=False,
                      xaxis_title='Hourly Time Period',
                      yaxis_title=f'{company} Call Volume per Hour',
                     )
    fig.update_xaxes(tickangle=45,
                     tickfont={'size':10},
                    )
    return fig
    
def incident_times(gt_time,lt_time,company,df=df):
    # time1 and time2 are to be entered as a string in the format 'HH:MM' 24 hr time (military time)
    # and times must be in range 00:00 to 23:59. 
       
    company = company.upper()
    if company != 'ALL':
        time_range = df[(df.Units.str.contains(company)) & (df.Time>gt_time) & (df.Time<lt_time)]
        mapper = time_range.Call_Type.unique().tolist()
        fig = px.histogram(time_range,
                           x='Call_Type',
                           color='Call_Type',
                           color_discrete_map=graph_colors(time_range.Call_Type.unique().tolist(),
                                                           len(time_range.Call_Type.unique()),
                                                           color='green'),
                           title=f"Incident Type and Count for {company} between the hours of {gt_time} and {lt_time}",
                           height=800,
                           width=1000,
                          )
        fig.update_layout(showlegend=False,
                          xaxis_title='Incident Type',
                          yaxis_title='Total Number of Incidents',
                         )
        fig.update_xaxes(tickangle=45,
                         tickfont={'size':10},
                        )
        return fig
    else:
        time_range = df[(df.Time>gt_time) & (df.Time<lt_time)]
        mapper = time_range.Call_Type.unique().tolist()
        fig = px.histogram(time_range,
                           x='Call_Type',
                           color='Call_Type',
                           color_discrete_map=graph_colors(time_range.Call_Type.unique().tolist(),
                                                           len(time_range.Call_Type.unique()),
                                                           color='green'),
                           title=f"Incident Type and Count for All Units between the hours of {gt_time} and {lt_time}",
                           height=800,
                           width=1000,
                          )
        fig.update_layout(showlegend=False,
                          xaxis_title='Incident Type',
                          yaxis_title='Total Number of Incidents',
                         )
        fig.update_xaxes(tickangle=45,
                         tickfont={'size':10},
                        )
        return fig

# ~~ CAN ADD CODE HERE TO FURTHER DEFINE THE DATAFRAME USED IN THE FUNCTION ~~
# to run monthly incidents for specific companies for example: 'df = df[df.Units.str.contains('E22')]
def monthly_incidents(month,company,df=df):
    company = company.upper()
    
    month = month.capitalize()
    month_dict = {'January':'01',
                  'February':'02',
                  'March':'03',
                  'April':'04',
                  'May':'05',
                  'June':'06',
                  'July':'07',
                  'August':'08',
                  'September':'09',
                  'October':'10',
                  'November':'11',
                  'December':'12'}
    
    monthly_df = df[df.Date.str.contains('2023-'+month_dict[month])]
    
    # Lat/Long of each station to center the map for a companies primary response district
    district = {'HQ':(41.393510,-73.455480),
                'E23':(41.407951,-73.436729),
                'E24':(41.413050,-73.422240),
                'E25':(41.427157,-73.504407),
                'E26':(41.373615,-73.487025)}
    if company not in ['E23','E24','E25','E26']:
        lat = district['HQ'][0]
        long = district['HQ'][1]
    else:
        lat=district[company][0]
        long=district[company][1]
    
    if company=='ALL':
        fig = px.density_mapbox(monthly_df,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Call_Type','Call_Location','Units'],
                                center={'lat':lat,'lon':long},
                                color_continuous_scale=px.colors.sequential.solar,
                                zoom=10,
                                mapbox_style='open-street-map',
                                radius=7,
                                title=f"Incident Volume by Address for the month of {month}",
                                height=800,
                                width=800,
                               )
        return fig 
    else:
        monthly_df = monthly_df[monthly_df.Units.str.contains(company)]
        fig = px.density_mapbox(monthly_df,
                                lat='Latitude',
                                lon='Longitude',
                                hover_data=['Call_Type','Call_Location','Units'],
                                center={'lat':lat,'lon':long},
                                color_continuous_scale=px.colors.sequential.solar,
                                zoom=12,
                                mapbox_style='open-street-map',
                                radius=7,
                                title=f"{company} Incident Volume by Address for the month of {month}",
                                height=800,
                                width=800,
                               )
        return fig



# create a list that contains the units we're interested in getting call totals from...
all_units = ['TAC1','SQ21','E22','E23','E24','E25','E26','T1','C30']

# ... and a list of all call types any of the companies may have responded too.
incident_type_list = df.Call_Type.unique().tolist()

# Create a dataframe to house total run numbers
run_num_df = pd.DataFrame(np.zeros((len(incident_type_list),len(all_units))),
                          index=incident_type_list,
                          columns=all_units)
# add the type of call as a column at the beginning of the dataframe
run_num_df.insert(0,"Call_Type",incident_type_list)
run_num_df = run_num_df.copy()

# function to help get incident/call types specific to each company
def comp_calltype (unit,call,df=df):
    comp_calltype_df = df[(df.Units.str.contains(unit)) & (df.Call_Type==call)]
    return comp_calltype_df

# use the above function to populate the run_num_df with the number of runs per call type per company
for company in all_units:
    for call in incident_type_list:
        count = comp_calltype(company,call).Call_Type.count()
        run_num_df.loc[call,company]=count

# run_num_df is now populate with the total number of runs per call type per company

app = Dash(__name__,prevent_initial_callbacks=False)

app.layout = html.Div([
    html.Div([html.H1("Danbury Fire Department Incident Survey Analysis",style={'fontFamily':'Engravers MT',
                                                                               'color':'#cc0000'}),
              html.P("""
              Analysis of incident types by location, responding company, and time across the City of
              Danbury. This will show graphical representation of call types call volume, frequented 
              response locations, as well as their relationship and correlation.
              """,),
              html.P("""
              This analysis will center on the day to day, active, career fire companies. It will categorize
              and plot responses to various incidents and locations. Below, you first find a table showing all 
              of the various incident (calls) types that each of the units ('companies') has responded too.
              """),            
             ],style = {'font-family':'Arial', 'textAlign':'center'},
             id='page_header'),
    html.Br(),
    html.Div([
        dash_table.DataTable(id='datatable-interactive',
                             data=run_num_df.to_dict('records'),#'records' orients the dict as a list of dicts
                             columns=[{'name':i,'id':i} for i in run_num_df.columns],# identifiers for DataTable
                             editable=True,
                             filter_action='native',
                             sort_action='native',
                             sort_mode='single',
                             column_selectable='multi',
                             row_selectable='multi',
                             selected_columns=[],
                             selected_rows=[],
                             page_action='native',
                             page_current=0,
                             page_size=5,
                             style_cell= {
                                 'minWidth':100,
                                 'maxWidth':100,
                                 'width':100},
                             style_filter={'backgroundColor':'rgb(225,225,225)',
                                           'border':'2px solid black'},
                             style_header={'backgroundColor':'rgb(100,100,100)',
                                           'color':'white'},
                             style_data={'color':'white',
                                         'backgroundColor':'rgb(50,50,50)',
                                         'whiteSpace':'normal',
                                         'height':'auto'},
                             style_cell_conditional=[{'textAlign':'center'}],
                             #style_data_conditional=[{
                             #    'if': {'row_index': 'odd'},
                             #    'backgroundColor': 'rgb(220, 220, 220)'}],
                             ),
    ]),
    html.Br(),
    html.Div([
        html.Div([
            dcc.Dropdown(options=companies,
                         value='ALL',
                         placeholder='Select Company',
                         id='companies'),
        ],style={'width':300},
        ),
        html.Div([
            dcc.Graph(id='bar-chart'), # bar chart
            html.Br(),
            html.Div([
                dcc.Graph(id='density-map'), # density heat map
                dcc.Graph(id='hourly-volume'), # bar chart of call volume by hour
            ],style={'display':'flex'},),
        ])
    ]),
    html.Br(),html.Br(),
    html.Div([
        dcc.Dropdown(options=times,
                     value='07:00',
                     placeholder='Enter time',
                     id='start-time',
                     style=dict(width='50%')), # menu of avialable start times
        dcc.Dropdown(options=times,
                     value='17:00',
                     placeholder='Enter Time',
                     id='end-time',
                     style=dict(width='50%')), # menu of available end times
        dcc.Dropdown(options=months,
                     value='December',
                     placeholder='Enter a Month',
                     id='period-month',
                     style=dict(width='50%')), # menu of 12 months
        dcc.Dropdown(options=companies,
                     value='ALL',
                     placeholder='Enter Company',
                     id='company',
                     style=dict(width='50%')), # companies for time and period input
    ],
        style={'display':'flex',}
    ),
    html.Div([
        dcc.Graph(id='time-chart'), # incident occurence during time periods
        dcc.Graph(id='month-chart') # incident total by month
    ],style={'display':'flex'},
    ),
])

@app.callback(
    [Output(component_id='bar-chart',component_property='figure'),
     Output(component_id='density-map',component_property='figure'),
     Output(component_id='hourly-volume',component_property='figure')],
    Input(component_id='companies',component_property='value'),
)
def response_graphs(company):
        return [calls_by_company(company),company_heatmap(company),hourly_incident_volume(company)]

@app.callback(
    [Output(component_id='time-chart',component_property='figure'),
     Output(component_id='month-chart',component_property='figure'),],
    [Input(component_id='start-time',component_property='value'),
     Input(component_id='end-time',component_property='value'),
     Input(component_id='period-month',component_property='value'),
     Input(component_id='company',component_property='value'),],
)
def time_graphs(start_time,end_time,month,company):
    return [incident_times(start_time,end_time,company),monthly_incidents(month,company)]
            
if __name__ == '__main__':
    app.run(debug=True)
