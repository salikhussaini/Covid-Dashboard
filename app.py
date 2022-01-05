import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import plotly.graph_objects as go # Plotting
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import zipfile

st.set_page_config(page_title="Covid Dashboard", page_icon="🐞", layout="centered")

@st.cache 
def get_data():
    a = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us.csv')
    b = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
    c = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    c['State_County'] = c['state'] + "|" + c['county']
    return(a,b,c)
@st.cache 
def get_list():
    df_us, df_state,df_county =  get_data()
    states = df_state['state'].unique()
    counties = df_county['State_County'].unique()
    return(states,counties)
@st.cache 
def agg():
    df_us, df_state,df_county =  get_data()
    last_day = df_us.date.max()
    df_us = df_us[df_us['date'] == last_day]
    df_state = df_state[df_state['date'] == last_day]
    df_county = df_county[df_county['date'] == last_day]
    return(df_us, df_state,df_county)
@st.cache 
def load_agg():
    US_diff = pd.read_csv('Data/US_diff.csv')
    US_diff = US_diff.iloc[:,1:]  
    State_diff = pd.read_csv('Data/State_diff.csv')
    State_diff = State_diff.iloc[:,1:]

    path_to_zip_file = 'Data/County_diff.zip'
    directory_to_extract_to = 'Data/'

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)

    County_diff = pd.read_csv('Data/County_diff.csv')
    County_diff = County_diff.iloc[:,1:]

    return(US_diff,State_diff,County_diff)

df_us,df_state,df_county =  get_data()
latest_us, latest_state, latest_county = agg() 
df_states_list,df_counties_list =  get_list()
US_diff,State_diff,County_diff = load_agg()


def add_diff(US_diff,State_diff,County_diff,df_us,df_state,df_county):
    last_day_agg = US_diff.date.max()
    df_us_1 = df_us[df_us.date > last_day_agg]

    a2 = US_diff.tail(3).append(df_us_1, ignore_index = True)
    a2['cases_dif'] = a2.cases.diff()
    a2['deaths_dif'] = a2.deaths.diff()
    US_diff = US_diff.append(a2[a2.date > last_day_agg])
    
    return(US_diff)

US_diff = add_diff(US_diff,State_diff,County_diff,df_us,df_state,df_county)

st.title("🐞 Covid Dashboard!")
Option =  st.sidebar.\
    selectbox("How many States would you want to look at?",\
        ['Global', 'Country', 'State','County'])

if Option == 'Country':
    #Time-Series Graph: Covid Cases and Deaths in the US
    with st.container():
        new_cases = US_diff['cases_dif'].tail(1).values[0]
        new_cases_5 = US_diff['cases_dif'].tail(5).sum()
        new_cases_5_mean = US_diff['cases_dif'].tail(5).mean()

        new_deaths = US_diff['deaths_dif'].tail(1).values[0]
        new_deaths_5 = US_diff['deaths_dif'].tail(5).sum()
        new_deaths_5_mean = US_diff['deaths_dif'].tail(5).mean()

        col1, col2, col3  = st.columns(3)
        with col1:
            st.write('New Cases in last day: {}'.format(new_cases))
        with col2:
            st.write('New Cases in 5 last days: {}'.format(new_cases_5))
        with col3:
            st.write('Mean New Cases in 5 last days: {}'.format(new_cases_5_mean))

        col4, col5, col6 = st.columns(3)
        with col4:
            st.write('New Deaths in last day: {}'.format(new_deaths))
        with col5:
            st.write('New Deaths in 5 last days: {}'.format(new_deaths_5))
        with col6:
            st.write('MeanNew Deaths in 5 last days: {}'.format(new_deaths_5_mean))
    with st.container():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=['Covid Cases in US', 'Covid Deaths in US'])
        fig.add_trace(
            go.Line(x= df_us['date'], y= df_us['cases'], name='Cases',showlegend=False)
            ,row=1, col=1)
        fig.add_trace(
            go.Line(x= df_us['date'], y= df_us['deaths'], name='Deaths',showlegend=False)
            ,row=2, col=1)
        fig.update_layout({'title': {'text': 'Covid Cases and Deaths in the US', 'x': .5, 'y': .9}})
        st.plotly_chart(fig, True)
    #Histogrm: Covid Cases and Deaths in the US
    with st.container():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=['Covid Cases in US', 'Covid Deaths in US'])
        fig.add_trace(
            go.Bar(x= US_diff['date'], y= US_diff['cases_dif'], name='Cases',showlegend=False)
            ,row=1, col=1)
        fig.add_trace(
            go.Bar(x= US_diff['date'], y= US_diff['deaths_dif'], name='Deaths',showlegend=False)
            ,row=2, col=1)
        fig.update_layout({'title': {'text': 'Covid Cases and Deaths in the US', 'x': .5, 'y': .9}})
        st.plotly_chart(fig, True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.pie(latest_state ,\
                labels = 'state', values = 'cases',\
                    hover_name="state",\
                        hover_data=["cases"],\
                            title="Covid Cases in US by State")
            fig2.update_traces(text = latest_state['state'],textinfo='text+percent',  textposition='inside')

            st.plotly_chart(fig2, True)
        with col2:
            fig2 = px.pie(latest_state ,\
                labels = 'state', values = 'deaths',\
                    hover_name="state",\
                        hover_data=["deaths"],\
                            title="Covid Deaths in US by State")
            fig2.update_traces(text = latest_state['state'],textinfo='text+percent',  textposition='inside')

            st.plotly_chart(fig2, True)


elif Option == 'State': 
    State = st.sidebar.selectbox\
        ("Choose a state", df_states_list)

    df = df_state[df_state.state == State]
    state_diff_1 = State_diff[State_diff.state == State]

    with st.container():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=['Covid Cases in US', 'Covid Deaths in US'])
        fig.add_trace(
            go.Line(x= df['date'], y= df['cases'], name='Cases',showlegend=False)
            ,row=1, col=1)
        fig.add_trace(
            go.Line(x= df['date'], y= df['deaths'], name='Deaths',showlegend=False)
            ,row=2, col=1)
        fig.update_layout({'title': {'text': 'Covid Cases and Deaths in the US', 'x': .5, 'y': .9}})
        st.plotly_chart(fig, True)
    
    with st.container():
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,subplot_titles=['Covid Cases in US', 'Covid Deaths in US'])
        fig.add_trace(
            go.Bar(x= state_diff_1['date'], y= state_diff_1['cases_dif'], name='Cases',showlegend=False)
            ,row=1, col=1)
        fig.add_trace(
            go.Bar(x= state_diff_1['date'], y= state_diff_1['deaths_dif'], name='Deaths',showlegend=False)
            ,row=2, col=1)
        fig.update_layout({'title': {'text': 'Covid Cases and Deaths in the US', 'x': .5, 'y': .9}})
        st.plotly_chart(fig, True)

