from datetime import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import plotly.graph_objects as go # Plotting
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from urllib.request import urlopen
import json
import zipfile

st.set_page_config(page_title="Covid Dashboard", page_icon="🐞", layout="centered")

st.cache()
def get_data():
    path_to_zip_file = 'Data/US.zip'
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        files = zip_ref.namelist()
        files_a = []
        for a in files:
            df = zip_ref.open(a)
            df = pd.read_csv(df)
            files_a.append(df)

        US,US_counties,US_states = (files_a[0],files_a[1],files_a[2])
        US_counties['State_County'] = US_counties['state'] + "|" + US_counties['county']
        
    path_to_zip_file = 'Data/US_diff.zip'
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        files = zip_ref.namelist()
        files_a = []
        for a in files:
            df = zip_ref.open(a)
            df = pd.read_csv(df)
            files_a.append(df)

        US_counties_diff,US_states_diff,US_diff = (files_a[0],files_a[1],files_a[2])

    return(US,US_counties,US_states,US_diff,US_counties_diff,US_states_diff)
st.cache()
def get_list(df_state,df_county):
    states = df_state['state'].unique()
    counties = df_county['State_County'].unique()
    return(states,counties)
st.cache()
def agg(df_us, df_state,df_county):
    df_us['date'] = pd.to_datetime(df_us['date'])
    df_state['date'] = pd.to_datetime(df_state['date'])
    df_county['date'] = pd.to_datetime(df_county['date'])
    last_day = df_us.date.max()
    df_us_1 = df_us[df_us['date'] == last_day]
    df_state_1 = df_state[df_state['date'] == last_day]
    df_county_1 = df_county[df_county['date'] == last_day]
    return(df_us_1, df_state_1,df_county_1)
st.cache()
def load_agg(US_diff,State_diff,County_diff):
    US_diff = US_diff.iloc[:,1:]  
    State_diff = State_diff.iloc[:,1:]
    County_diff = County_diff.iloc[:,1:]

    return(US_diff,State_diff,County_diff)

df_us,df_county,df_state,US_diff,County_diff,State_diff = get_data()
latest_us, latest_state, latest_county = agg(df_us, df_state,df_county) 
df_states_list,df_counties_list =  get_list(df_state,df_county)
US_diff,State_diff,County_diff = load_agg(US_diff,State_diff,County_diff)

def add_diff(US_diff,State_diff,County_diff,df_us,df_state,df_county):
    if US_diff.date.max() == df_us.date.max():
        pass
    else:
        last_day_agg = US_diff.date.max()
        df_us_1 = df_us[df_us.date > last_day_agg]

        a2 = US_diff.tail(3).append(df_us_1, ignore_index = True)
        a2['cases_dif'] = a2.cases.diff()
        a2['deaths_dif'] = a2.deaths.diff()
        US_diff = US_diff.append(a2[a2.date > last_day_agg])

        return(US_diff)

st.title("🐞 Covid Dashboard!")
Option =  st.sidebar.\
    selectbox("Which Level would you want to look at?",\
        ['Global (Under Development)', 'Country', 'State',\
            'County (Under Development)'])

if Option == 'Country':
    #Written Info about how many cases & deaths
    with st.container():
        new_cases = US_diff['cases_dif'].tail(1).values[0]
        new_cases_5 = US_diff['cases_dif'].tail(5).sum()
        new_cases_5_mean = US_diff['cases_dif'].tail(5).mean()

        new_deaths = US_diff['deaths_dif'].tail(1).values[0]
        new_deaths_5 = US_diff['deaths_dif'].tail(5).sum()
        new_deaths_5_mean = US_diff['deaths_dif'].tail(5).mean()

        col1, col2, col3  = st.columns(3)
        with col1:
            st.write('New Cases in last day:\n{}'.format(new_cases))
        with col2:
            st.write('New Cases in 5 last days:\n{}'.format(new_cases_5))
        with col3:
            st.write('Mean New Cases in 5 last days:\n{}'.format(new_cases_5_mean))

        col4, col5, col6 = st.columns(3)
        with col4:
            st.write('New Deaths in last day:\n{}'.format(new_deaths))
        with col5:
            st.write('New Deaths in 5 last days:\n{}'.format(new_deaths_5))
        with col6:
            st.write('Mean New Deaths in 5 last days:\n{}'.format(new_deaths_5_mean))
    #Time-Series Graph: Covid Cases and Deaths in the US
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
    #PieChart: Covid Cases and Deaths in the US
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
    #BarChart: Top 10 States Covid Cases and Deaths in the US
    with st.container():
        col1, col2 = st.columns(2)
        death_10 = latest_state.sort_values('deaths',ascending=False)[['state','deaths']].head(10)
        cases_10 = latest_state.sort_values('cases',ascending=False)[['state','cases']].head(10)

        with col1:
            fig1 = px.bar(cases_10 ,\
                x = 'state', y = 'cases',\
                    hover_name="state",\
                        hover_data=["cases"],\
                            title="Top 10 States with most Covid Cases in US")
            st.plotly_chart(fig1, True)
        with col2:
            fig2 = px.bar(death_10 ,\
                x = 'state', y = 'deaths',\
                    hover_name="state",\
                        hover_data=["deaths"],\
                            title="Top 10 States with most Death Cases in US")

            st.plotly_chart(fig2, True)
    #BarChart: Top 10 States New Covid Cases and Deaths in the US
    with st.container():
        col3, col4 = st.columns(2)
        last_day_agg = State_diff.date.max()

        t_df = State_diff[State_diff['date'] == last_day_agg]
        t_death_10 = t_df.sort_values('deaths_dif',ascending=False)[['state','deaths_dif']].head(10)
        t_cases_10 = t_df.sort_values('cases_dif',ascending=False)[['state','cases_dif']].head(10)

        with col3:
            fig2a = px.bar(t_cases_10 ,\
                x = 'state', y = 'cases_dif',\
                    hover_name="state",\
                        hover_data=["cases_dif"],\
                            title="Top 10 States with most New Covid Cases in US")
            st.plotly_chart(fig2a, True)
        with col4:
            fig3a = px.bar(t_death_10 ,\
                x = 'state', y = 'deaths_dif',\
                    hover_name="state",\
                        hover_data=["deaths_dif"],\
                            title="Top 10 States with most New Death Cases in US")

            st.plotly_chart(fig3a, True)





elif Option == 'State': 
    State = st.sidebar.selectbox\
        ("Choose a state", df_states_list)

    df = df_state[df_state.state == State]
    state_diff_1 = State_diff[State_diff.state == State]
        #Written Info about how many cases & deaths
    with st.container():
        new_cases = state_diff_1['cases_dif'].tail(1).values[0]
        new_cases_5 = state_diff_1['cases_dif'].tail(5).sum()
        new_cases_5_mean = state_diff_1['cases_dif'].tail(5).mean()

        new_deaths = state_diff_1['deaths_dif'].tail(1).values[0]
        new_deaths_5 = state_diff_1['deaths_dif'].tail(5).sum()
        new_deaths_5_mean = state_diff_1['deaths_dif'].tail(5).mean()

        col1, col2, col3  = st.columns(3)
        with st.container():
            with col1:
                st.write('New Cases in last day:\n{}'.format(new_cases))
            with col2:
                st.write('New Cases in 5 last days:\n{}'.format(new_cases_5))
            with col3:
                st.write('Mean New Cases in 5 last days:\n{}'.format(new_cases_5_mean))

        col4, col5, col6 = st.columns(3)
        with st.container():
            with col4:
                st.write('New Deaths in last day:\n{}'.format(new_deaths))
            with col5:
                st.write('New Deaths in 5 last days:\n{}'.format(new_deaths_5))
            with col6:
                st.write('Mean New Deaths in 5 last days:\n{}'.format(new_deaths_5_mean))
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


