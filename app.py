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
    State_diff = pd.read_csv('Data/State_diff.csv')

    path_to_zip_file = 'Data/County_diff.zip'
    directory_to_extract_to = 'Data/'

    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
        
    County_diff = pd.read_csv('Data/County_diff.csv')

    return(US_diff,State_diff,County_diff)

df_us,df_state,df_county =  get_data()
latest_us, latest_state, latest_county = agg() 
df_states_list,df_counties_list =  get_list()
US_diff,State_diff,County_diff = load_agg()

st.title("🐞 Covid Dashboard!")
Option =  st.sidebar.\
    selectbox("How many States would you want to look at?", ['All', 'Some', 'One'])

if Option == 'All':
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

elif Option == 'Some': 
    States = st.sidebar.multiselect\
        ("Choose a state or states", df_states_list)
    with st.container():
        df = df_state[df_state.state.isin(States)]

        fig1 = px.line(df, x="date", y="cases", color='state')
        fig1.update_layout({'title': {'text': 'Covid Cases in the US by State', 'x': .5, 'y': .9}})
        st.plotly_chart(fig1, True)

        fig2 = px.line(df, x="date", y="deaths", color='state')
        fig2.update_layout({'title': {'text': 'Covid Deaths in the US by State', 'x': .5, 'y': .9}})
        st.plotly_chart(fig2, True)


if Option == 'One': 
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

