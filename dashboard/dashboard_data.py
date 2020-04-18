import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import settings

### data sources
BRASIL_IO_COVID19 = "https://brasil.io/dataset/covid19/caso?format=csv"
BRASIL_IO_CART = "https://brasil.io/dataset/covid19/obito_cartorio?format=csv"

@st.cache(ttl=settings.CACHE_TTL)
def get_data():
    brasil_io_url = BRASIL_IO_COVID19
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados", "deaths": "Mortes Acumuladas"})
    cases["date"] = pd.to_datetime(cases["date"])

    return cases

@st.cache(ttl=settings.CACHE_TTL)
def get_data_from_source(source,usecols=None,rename_cols=None):
    df = pd.read_csv(source,usecols=usecols)
    if rename_cols:
        df.rename(columns=rename_cols)
    df["date"] = pd.to_datetime(df["date"])    
    return df

@st.cache(suppress_st_warning=True, ttl=settings.CACHE_TTL, allow_output_mutation=True)
def get_data_uf(data, uf, city_options, variable):
    if uf:
        data = data.loc[data.state.isin(uf)]
        if city_options:
            region_name = "Cidade"
            city_options = [c.split(" - ")[1] for c in city_options]
            data = data.loc[
                (data.city.isin(city_options)) & (data.place_type == "city")
            ][["date", "state", "city", variable]]
            pivot_data = data.pivot_table(values=variable, index="date", columns="city")
            data = pd.DataFrame(pivot_data.to_records())
        else:
            region_name = "Estado"
            data = data.loc[data.place_type == "state"][["date", "state", variable]]
            pivot_data = data.pivot_table(values=variable, index="date", columns="state")
            data = pd.DataFrame(pivot_data.to_records())

    else:
        region_name = "Brasil"
        data = data.loc[data.place_type == "city"].groupby("date")[variable].sum().to_frame().reset_index()

    melted_data = pd.melt(
        data,
        id_vars=['date'],
        var_name=region_name,
        value_name=variable,
    )
    return region_name, melted_data

def get_data_cart(data, uf, variable):
    if uf:
        data = data.loc[data.state.isin(uf)]
        #if city_options:
        #    region_name = "Cidade"
        #    city_options = [c.split(" - ")[1] for c in city_options]
        #    data = data.loc[
        #        (data.city.isin(city_options)) & (data.place_type == "city")
        #    ][["date", "state", "city", variable]]
        #    pivot_data = data.pivot_table(values=variable, index="date", columns="city")
        #    data = pd.DataFrame(pivot_data.to_records())
        #else:
        region_name = "Estado"
        data = data.loc[:,["date", "state", variable]]
        pivot_data = data.pivot_table(values=variable, index="date", columns="state")
        data = pd.DataFrame(pivot_data.to_records())
    else:
        region_name = "Brasil"
        data = data.groupby("date")[variable].sum().to_frame().reset_index()

    melted_data = pd.melt(
        data,
        id_vars=['date'],
        var_name=region_name,
        value_name=variable,
    )
    return region_name, melted_data


def plot_series(data, x_variable, y_variable, region_name, is_log):
    if is_log:
        data = data.copy()
        log_y_variable = f"Log[{y_variable}]"
        data[log_y_variable] = np.log(data[y_variable] + 1)
        y_variable = log_y_variable

    fig = px.scatter(data, x=x_variable, y=y_variable, color=region_name)    
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Indivíduos",
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",        
    )
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    
    return fig

def add_series(fig, data, x_variable, y_variable, region_name, is_log):    
    
    if is_log:
        data = data.copy()
        log_y_variable = f"Log[{y_variable}]"
        data[log_y_variable] = np.log(data[y_variable] + 1)
        y_variable = log_y_variable
    # Need to fix color 
    
    if region_name == 'Brasil':
        fig.add_scatter(x=data[x_variable], y=data[y_variable], name=y_variable,
                        hovertemplate="Mortes Acumuladas: %{y:.2f} Data: %{x}",
                        )
    else:        
        for region in list(data[region_name].unique()):
            plot_df = data.loc[data[region_name] == region]                        
            fig.add_scatter(x=plot_df[x_variable], y=plot_df[y_variable], name='Mortes ' + region,
                        hovertemplate="Mortes Acumuladas: %{y:.2f} Data: %{x}",
                        )            
    
    fig.update_traces(mode='lines+markers')
    fig.update_layout(        
        xaxis_title="Data",
        yaxis_title="Indivíduos",
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",        
    )
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    return fig


@st.cache(ttl=settings.CACHE_TTL)
def get_aligned_data(df,align=100):
    align_dfs = [df.loc[df[c]>=100,[c]].values.reshape(-1,) for c in df.columns]
    columns = [c for c in df.columns]
    aligned_df = pd.DataFrame(align_dfs,index=columns).T
    #align_dfs = [d.reset_index() for d in align_dfs]
    #aligned = pd.concat([d for d in align_dfs],ignore_index=True)
    return aligned_df

@st.cache(ttl=settings.CACHE_TTL)
def get_city_list(data, uf):
    data_filt = data.loc[(data.state.isin(uf)) & (data.place_type == "city")]
    data_filt["state_city"] = data_filt["state"] + " - " + data_filt["city"]
    return sorted(list(data_filt.state_city.drop_duplicates().values))


def _translate(country_name, names):
    if country_name in names:
        return names[country_name]
    else:
        return country_name


@st.cache(ttl=settings.CACHE_TTL)
def get_global_cases():
    url = (
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_"
        "confirmed_global.csv"
    )
    country_names = json.load(open("dashboard/nomes-paises.json"))
    global_cases = pd.read_csv(url)
    global_cases["Country/Region"] = global_cases["Country/Region"]\
        .map(lambda x: _translate(x, country_names))
    global_cases = global_cases.rename(columns={"Country/Region": "País/Região"})
    return global_cases


@st.cache(ttl=settings.CACHE_TTL)
def get_countries_list(data):
    return sorted(list(data["País/Região"].drop_duplicates()))


@st.cache(suppress_st_warning=True)
def get_countries_data(data, countries):
    if countries:
        region_name = "País/Região"
        result = data.loc[data[region_name].isin(countries)]\
            .groupby([region_name, "Data"]).sum().reset_index()
    else:
        region_name = None
        result = data.groupby("Data").sum().reset_index()
    return region_name, result


@st.cache(persist=True, allow_output_mutation=True, ttl=settings.CACHE_TTL)
def load_lat_long():
    path_mapas = 'mapas/Estados.csv'
    return pd.read_csv(path_mapas)
