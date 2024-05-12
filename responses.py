import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import dash    
from Incident_Data import IncidentData
from dash import  html, dcc, Output, Input

# Create a dataframe which includes Call Types, Units, Call Locations, Call Date and Time,
# and includes latitude and longitude with the associated incident addresses.
# The CSV file was created in Jupyter Labs from First Due Software utilized by the
# Danbury Fire Department. The calls were imported from First Due starting in April 2023 up to 
# the end of the year 2023. The software was first implemented in the Spring of 2023.
# The Data was extracted, transformed, and built into a dataframe using the Pandas library,
# and was then saved into a CSV file for use in this application. This application will show 
# various data points regarding those responses including total number of calls, call density in 
# throughout the City of Danbury, and distribution of those calls.

# #0f2537 SUPERHERO body bg color (grayish blue)

# ~~~~~ DASH BOOTSTRAP THEME LAYOUT ~~~~~

app = dash.Dash(__name__,
           prevent_initial_callbacks=False,
           external_stylesheets=[dbc.themes.SUPERHERO])


# Mapper for graph colors
def graph_colors(df_graph_category,len_df_category,color='red'):
    
    red = px.colors.n_colors('rgb(165,0,0)','rgb(255,0,0)',len_df_category,colortype='rgb')
    blue = px.colors.n_colors('rgb(0,0.001,150)','rgb(0,150,150)',len_df_category,colortype='rgb')
    green = px.colors.n_colors('rgb(0,150,.001)','rgb(0,125,125)',len_df_category,colortype='rgb')
    yellow = px.colors.n_colors('rgb(255,255,0)','rgb(255,125,0)',len_df_category,colortype='rgb')
    dark_blue = px.colors.n_colors('rgb(.001,.001,75)','rgb(50,50,200)',len_df_category,colortype='rgb')
    red_blue = px.colors.n_colors('rgb(255,.001,.001)','rgb(.001,.001,255)',len_df_category,colortype='rgb')
    green_blue = px.colors.n_colors('rgb(0,255,.001)','rgb(0,.001,255)',len_df_category,colortype='rgb')
    
    color_list = {'red':red,'blue':blue,'green':green,'yellow':yellow,'dark_blue':dark_blue,
                 'rd_bl':red_blue,'gr_bl':green_blue}

    mapper = {x:y for x,y in zip(df_graph_category,color_list[color])}
    return mapper
# DFD list of Career Division fire companies
companies = ['ALL','C30','T1','TAC1','SQ21','E22','E23','E24','E25','E26']

# list of times for dropdown menus
times = ['--']
times.extend([f'0{x}:00:00' if x < 10 else f'{x}:00:00' for x in range(24)])

hours = ['--']
hours.extend([f'0{x}:00 hrs' if x < 10 else f'{x}:00 hrs' for x in range(24)])

hours_dict = {x:y for x,y in zip(hours,times)}

# list of month's to use in dictionary for dropdown menus
monthname = ['--','January','February','March','April','May','June','July','August',
                  'September','October','November','December']
# dicitonary to pair month name with month number to use in IncidentData() values
months = {m:int(i) for m,i in zip(monthname,list(range(0,13)))}

#  Data for sidebar tables and pie charts
df1 = IncidentData('','','').all()  
df1['LOCATION'] = df1.LOCATION.apply([lambda x: x[:-11]]) 

dfu = IncidentData('','','').unit_df()
dfu.index.name = 'Incident Date & Time'

total_calls = pd.Series([dfu[x].sum() for x in dfu.columns],index=dfu.columns)
total_calls.index.name = 'Unit'

loc_count = df1.iloc[:,1].value_counts()[df1.iloc[:,1].value_counts()>14]
loc_count.index.name = 'Location'
loc_count_dict = {k:v for k,v in zip(loc_count.index,range(len(loc_count.index)))}
type_count = df1.iloc[:,2].value_counts()[df1.iloc[:,2].value_counts()>14]
type_count.index.name = 'Response Type'




# ~~~~~~~~ Application Layout ~~~~~~~~~
app.layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col(
                #html.Img(src="~/Danbury_FD_Seal.jpg",style={'width':150,'height':150}),
                lg=1),
            dbc.Col(
                dbc.Stack([# Header
                    html.H1("DANBURY FIRE DEPARTMENT RESPONSE DASHBOARD",
                            style={'color':'#df6919'}),
                    html.P(# dashboard description
                    """
                    This is a dashboard application to showcase Fire Department response data 
                    for the City of Danbury. Select parameters to show response data for various
                    time periods, month, and/or DFD Career Division unit. The City has a 
                    Shift Commander/Command Car, 5 engine companies, 1 Squad/Rescue, 1 Truck compnay, 
                    and 1 Tactical Unit.
                    """,
                    style={'color':'#abb6c2'}),
                    ]),lg=8,style={'textAlign':'center'},
                    ),
            dbc.Col(
                    #html.Img(src="~/DFD_Patch_v2.jpg",style={'width':150,'height':150}),
                        lg=1),
                ],class_name= 'p-3',
                justify='between'),
        ]),
# ~~~~~ DROP DOWN MENUS ~~~~~
    html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Select a Start Time"),
                        style={'textAlign':'center'}),
                    dbc.CardBody(
                        dcc.Dropdown(options=hours,
                                value=hours[0],
                                clearable=False,
                                id='time1'), 
                        class_name='text-dark'),
                    ],class_name='bg-primary border-rounded'),
                lg=2, width={'offset':1}),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Select an End Time"),
                        style={'textAlign':'center'}),
                    dbc.CardBody(
                        dcc.Dropdown(options=hours,
                                value=hours[0],
                                clearable=False,
                                id='time2'),                           
                        class_name='text-dark'),
                    ],class_name='bg-primary border-rounded'),                
                lg=2),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Select a Month"),
                        style={'textAlign':'center'}),
                    dbc.CardBody(
                        dcc.Dropdown(options=monthname,
                                value=monthname[0],
                                clearable=False,
                                id='month'),
                        class_name='text-dark'),
                    ],class_name='bg-primary border-rounded'),
                lg=2),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        html.H5("Select a DFD Unit"),
                        style={'textAlign':'center'}),
                    dbc.CardBody(
                        dcc.Dropdown(options=companies,
                                value=companies[0],
                                clearable=False,
                                id='company'),                            
                        class_name='text-dark'),
                    ],class_name='bg-primary border-rounded'),
                lg=2),
            ], justify='center'),
        ],),
    html.Div([
        dbc.Row([
            dbc.Col( # Card Stack
                dbc.Stack([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Total Responses by Unit"),
                            class_name='text-body'
                                ), 
                        dbc.CardBody(
                            dbc.Table.from_dataframe(total_calls,
                                                     striped=True,
                                                     bordered=True,
                                                     hover=True,
                                                     index=True),
                            class_name='bg-light'),
                        ], class_name= 'card-text-body bg-primary card-header'),
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Top 7 Response Locations"),
                            class_name='text-body'),
                        dbc.CardBody(
                            dbc.Table.from_dataframe(loc_count.head(7),
                                                     striped=True,
                                                     bordered=True,
                                                     hover=True,
                                                     index=True),
                            class_name='bg-light'),
                        ],class_name= 'card-text-body bg-primary card-header'),
                    dbc.Card([
                        dbc.CardHeader(
                            html.H5("Top 7 Response Types"),
                            class_name='text-bdoy'
                            ),
                        dbc.CardBody(
                            dbc.Table.from_dataframe(type_count.head(7),
                                                     striped=True,
                                                     bordered=True,
                                                     hover=True,
                                                     index=True),
                            class_name='bg-light'),
                        ],class_name= 'card-text-body bg-primary card-header'),
                    ],gap=2),
                lg = 2),
        dbc.Col( # main panel
            dbc.Row([ 
                dbc.Col(# Graphs
                    dbc.Stack([
                        dcc.Graph(id="densitymap"),
                        dcc.Graph(id='incidentlocation'),
                        dbc.Row(
                            dbc.Col(
                                dbc.Card([
                                    dbc.CardHeader(
                                        html.H5("Select one of the Frequently Responded Locations",
                                                style={'textAlign':'center'}),
                                        class_name='card-text-body bg-primary'),
                                    dbc.CardBody([
                                        dcc.Dropdown(options=loc_count.index,
                                                    value=loc_count.index[0],
                                                    clearable=False,
                                                    maxHeight=105,
                                                    id='freq_loc'),
                                        html.Br(),
                                        html.H6("""
                                            Each of the above locations has had at least 15 Fire Department
                                            responses over the past year. Select a location to view the 
                                            breakdown and number of specific incident types.""",
                                            style={'color':'rgb(255,255,255)'}),
                                        ],class_name='text-dark bg-primary'),
                                    ]),lg=10,width={'offset':1},
                                class_name='pt-5 border-primary'),
                            ),
                        dbc.Row(
                            dbc.Col([
                                dbc.CardGroup([
                                    dbc.Card(
                                        dbc.CardBody([
                                            html.P("Total Number of Incidents at",
                                                    style={'textAlign':'center',
                                                        'fontSize': 20}),
                                            html.P(id='total_calls_loc',
                                                    style={'textAlign':'center',
                                                        'fontSize':22})
                                            ],class_name='m-3 card-text-body bg-dark',
                                            ),class_name='bg-primary border-primary'),
                                    dbc.Card(
                                        dbc.CardBody([
                                            html.Br(),
                                            html.P(id='total_incidents',
                                                style={'fontSize':54,
                                                        'fontWeight':'bold',
                                                        'textAlign':'center'}),
                                            ],class_name='m-3 bg-dark'),
                                        class_name='bg-primary text-body border-primary'),
                                    ],class_name='border-primary'),
                                ],lg=10,width={'offset':1}),
                            class_name='pt-2 border-primary'),
                        ]),
                        class_name='p-1 d-flex justify-content-start',
                        lg = 5),
                dbc.Col(
                    dbc.Stack([
                        dcc.Graph(id='incidenttype'),
                        dcc.Graph(id='timeperiod'),
                        dcc.Graph(id='pie_freq_loc_type'),
                        ]),
                    class_name='p-1 d-flex justify-content-start',
                    width={'offset':1},
                    lg = 5,),
                ]),
            ),
        ]),
    ]),
],fluid=True)

# ##### FIRST GRAPH STACK #####
#~~~~~ Heat Density Map ~~~~~
def incident_heat_map(df_dhm,unit): 
    district = {'HQ':(41.393510,-73.455480),
                'E23':(41.407951,-73.436729),
                'E24':(41.413050,-73.422240),
                'E25':(41.427157,-73.504407),
                'E26':(41.373615,-73.487025)}

    if unit not in companies[1:]:
        df_dhm = df_dhm.all()
        t = "Incident Concentrations for the City of Danbury"    
    else:
        df_dhm = df_dhm.company(unit)
        t = f'Incident Concentration for {unit}'
    
    if unit not in ['E23','E24','E25','E26']:
        latt = district['HQ'][0]
        long = district['HQ'][1]
        z=11
        r=6
    else:
        latt=district[unit][0]
        long=district[unit][1]
        z=12
        r=8
        
    map = px.density_mapbox(data_frame=df_dhm,
                            lat='LATITUDE',
                            lon='LONGITUDE',
                            hover_data=['TYPE','ADDRESS'],
                            center={'lat':latt,'lon':long},
                            color_continuous_scale=px.colors.sequential.ice,
                            zoom=z,
                            mapbox_style='open-street-map',
                            radius=r,
                            title=t,
                            height=600,
                            width=800,) 
    map.update_layout(coloraxis_showscale=False,
                      title={'x':.5,'xref':'paper','xanchor':'auto'},
                      font={'color':'rgb(255,255,255)'},
                      paper_bgcolor='#0f2537')
    return map


@app.callback(
    Output(component_id='densitymap',component_property='figure'),
    Input(component_id='time1',component_property='value'),
    Input(component_id='time2',component_property='value'),
    Input(component_id='month',component_property='value'),
    Input(component_id='company',component_property='value'))
def density_map(time1_value,time2_value,month_value,company_value):
    d_map = incident_heat_map(IncidentData(hours_dict[time1_value],
                                            hours_dict[time2_value],
                                            months[month_value]),
                                            company_value)

    return d_map

# ~~~~~ Incident Location Totals ~~~~~

def incident_locations(df_lbar,unit,t1,t2,mon):
        
    if t1 not in times[1:] and t2 not in times[1:] and mon not in monthname[1:]:
        if unit not in companies[1:]:
            df_lbar = df_lbar.all()
            v_c = df_lbar['LOCATION'].value_counts()[df_lbar['LOCATION'].value_counts()>=20]
            t='Total Number of Incidents per Location with 20 or more Responses'
        else:
            df_lbar= df_lbar.company(unit)
            v_c = df_lbar['LOCATION'].value_counts()[df_lbar['LOCATION'].value_counts()>=5]
            t = f'Total Number of Responses per Location by {unit} with 5 or more Responses'
    else:
        if unit not in companies[1:]:
            df_lbar = df_lbar.all()
            v_c = df_lbar['LOCATION'].value_counts()
            t = 'Total Number of Responses per Location'
        else:
            df_lbar = df_lbar.company(unit)
            v_c = df_lbar['LOCATION'].value_counts()
            t = f'Total Number of Responses per Location by {unit}'
        
    bargraph = px.bar(data_frame=v_c,
                      x=v_c.index,
                      y=v_c,
                      color=v_c.index,
                      color_discrete_map=graph_colors(v_c.index,len(v_c.index),color='dark_blue'),
                      title=t,
                      height=600,
                      width=800)
    bargraph.update_xaxes(tickangle=45,
                          tickfont=dict(size=10))
    bargraph.update_layout(yaxis_title='Total Incidents to Location',
                        xaxis_title='Location',
                        showlegend=False,
                        title={'x':.5,'xref':'paper','xanchor':'auto'},
                        font={'color':'rgb(255,255,255)'},
                        paper_bgcolor='#0f2537',
                        plot_bgcolor='#abb6c2')    
    return bargraph



@app.callback(
    Output(component_id='incidentlocation',component_property='figure'),
    Input(component_id='time1',component_property='value'),
    Input(component_id='time2',component_property='value'),
    Input(component_id='month',component_property='value'),
    Input(component_id='company',component_property='value'))
def location_bargraph(time1_value,time2_value,month_value,company_value):
    l_bar = incident_locations(IncidentData(hours_dict[time1_value],
                                            hours_dict[time2_value],
                                            months[month_value]),
                                            company_value,
                                            time1_value,
                                            time2_value,
                                            month_value)

    return l_bar

@app.callback(
    Output(component_id='total_calls_loc',component_property='children'),
    Input(component_id='freq_loc',component_property='value'))
def total_calls(freqloc):
    return freqloc

@app.callback(
    Output(component_id='total_incidents',component_property='children'),
    Input(component_id='freq_loc',component_property='value'))
def number_total_loc(freqloc):
    return loc_count.iloc[loc_count_dict[freqloc]]


# ##### SECOND GRAPH STACK #####
# ~~~~~~ Incident Type Totals ~~~~~~
def incident_type_total(df_tth,unit):
    if unit in companies[1:]:
        df_tth = df_tth.company(unit)
        t = f"{unit} Incident Count by Type"   
    else:
        df_tth = df_tth.all()
        t = "Total Incidents for the Danbury Fire Department"
        
    histograph = px.histogram(data_frame=df_tth,
                              x='TYPE',
                              color='TYPE',
                              color_discrete_map=graph_colors(df_tth.TYPE.unique(),len(df_tth.TYPE.unique()),'green'),
                              title=t,
                              height=600,
                              width=800)
    histograph.update_layout(yaxis_title='Number of Incidents',
                            xaxis_title='Incident Type',
                            showlegend=False,
                            title={'x':.5,'xref':'paper','xanchor':'auto'},
                            font={'color':'rgb(255,255,255)'},
                            paper_bgcolor='#0f2537',
                            plot_bgcolor='#abb6c2')
    histograph.update_xaxes(tickangle=45,
                            tickfont=dict(size=10))
    return histograph


@app.callback(
    Output(component_id='incidenttype',component_property='figure'),
    Input(component_id='time1',component_property='value'),
    Input(component_id='time2',component_property='value'),
    Input(component_id='month',component_property='value'),
    Input(component_id='company',component_property='value'))
def type_histograph(time1_value, time2_value,month_value,company_value):
    t_histo = incident_type_total(IncidentData(hours_dict[time1_value],
                                                hours_dict[time2_value],
                                                months[month_value]),
                                                company_value)

    return t_histo

# ~~~~~ Time Period Incident Totals ~~~~~

def time_period_totals(df_tpt,unit,t1,t2,mon):
    # set IncidentData()
    if unit in companies[1:]:
        df_tpt = df_tpt.company(unit)
    else:
        df_tpt = df_tpt.all()

    if mon in monthname[1:] and t1 not in times[1:] and t2 not in times[1:]:
        if unit not in companies[1:]:
            t = f"Total Number of Incidents per Hourly Period for the Month of {mon}"
        else:
            t = f"Total Number of Incidents for {unit} per Hourly Period for the Month of {mon}"
    elif mon not in monthname[1:] and t1 not in times[1:] or t2 not in times[1:]:
        if unit not in companies[1:]:
            t = 'Total Number of Incidents per Hourly Period'
        else:
            t = f'Total Number of Incidents per Hourly Period for {unit}'
    else:
        if unit not in companies[1:]:
            t = f"Total Number of Incidents per Hourly Period from {t1} to {t2}"
        else:
            t = f"Total Number of Incidents per Hourly Period from {t1} to {t2} for {unit}"

    # hourly time periods and ranges
    daytimes = [f'0{x}:00' if x < 10 else f'{x}:00' for x in range(24)]
    hourly = [f'{daytimes[t-1]}-{daytimes[t]}' for t in range(1,len(daytimes))]
    hourly.append('23:00-00:00')

    # Total calls per hourly period
    periodtotalincidents = []
    for x in range(len(daytimes)):
        if x != 23:
            total_inc = df_tpt.iloc[df_tpt.index.indexer_between_time(daytimes[x],daytimes[x+1],include_end=False)].TYPE.count()
            periodtotalincidents.append(total_inc)
        else:
            total_inc = df_tpt.iloc[df_tpt.index.indexer_between_time(daytimes[x],'00:00:00',include_end=False)].TYPE.count()
            periodtotalincidents.append(total_inc)            
    periodtotalincidents = pd.Series(periodtotalincidents,index=hourly,name='Total')

    timegraph = px.bar(data_frame=periodtotalincidents,
                       x=periodtotalincidents.index,
                       y=periodtotalincidents,
                       color=periodtotalincidents.index,
                       color_discrete_map={i:'#cc0000' for i in periodtotalincidents.index},
                       title=t,
                       height=600,
                       width=800,)
    timegraph.update_layout(xaxis_title='Time Period',
                            yaxis_title='Total Incidents per Period',
                            showlegend=False,
                            title={'x':.5,'xref':'paper','xanchor':'auto'},
                            font={'color':'rgb(255,255,255)'},
                            paper_bgcolor='#0f2537',
                            plot_bgcolor='#abb6c2')
    timegraph.update_xaxes(tickangle=45,
                           tickfont=dict(size=12))
    return timegraph


@app.callback(
    Output(component_id='timeperiod',component_property='figure'),
    Input(component_id='time1',component_property='value'),
    Input(component_id='time2',component_property='value'),
    Input(component_id='month',component_property='value'),
    Input(component_id='company',component_property='value'))
def timeperiod_bargraph(time1_value,time2_value,month_value,company_value):
    tp_bar = time_period_totals(IncidentData(hours_dict[time1_value],
                                            hours_dict[time2_value],
                                            months[month_value]),
                                            company_value,
                                            time1_value,
                                            time2_value,
                                            month_value)

    return tp_bar

# ~~~~~ Pie Chart ~~~~~

def pie_location(i): 
    df_pie1 = IncidentData('','','').all()
    locations = df_pie1['LOCATION'].value_counts()[df_pie1['LOCATION'].value_counts()>14]
    loc_type = df_pie1[df_pie1['LOCATION'].str.contains(locations.index[i])]
    # those locations response types
    loc_pie = px.pie(loc_type,
                 names='TYPE',
                 color='TYPE',
                 color_discrete_sequence=px.colors.sequential.YlOrRd,
                 title=f'Types of Incident Responses to {locations.index[i]}',
                 height=600,
                 width=800)
    loc_pie.update_traces(textinfo='value')
    loc_pie.update_layout(legend_font=dict(size=10),
                          legend_y=.5,
                          font={'color':'rgb(255,255,255)'},
                          paper_bgcolor='#0f2537')
    
    return loc_pie

@app.callback(
    Output(component_id='pie_freq_loc_type',component_property='figure'),
    Input(component_id='freq_loc',component_property='value'))
def freq_loc_type(freqloc):
    loc_type_pie = pie_location(loc_count_dict[freqloc])

    return loc_type_pie

if __name__ == '__main__':
    app.run(debug=True)
