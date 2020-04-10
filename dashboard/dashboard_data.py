import json

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit import cache


@cache
def get_data():
    brasil_io_url = "https://brasil.io/dataset/covid19/caso?format=csv"
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados", "deaths": "Mortes Acumuladas"})
    cases["date"] = pd.to_datetime(cases["date"])

    return cases


@cache(suppress_st_warning=True)
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


def plot_series(data, x_variable, y_variable, region_name, is_log):
    if is_log:
        data = data.copy()
        log_y_variable = "Log[{}]".format(y_variable)
        data[log_y_variable] = np.log(data[y_variable] + 1)
        y_variable = log_y_variable

    fig = px.scatter(data, x=x_variable, y=y_variable, color=region_name)
    fig.update_traces(mode='lines+markers')
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Indivíduos",
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend_title="",
    )
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    st.plotly_chart(fig)


@cache
def get_aligned_data(df,align=100):
    align_dfs = [df.loc[df[c]>=100,[c]].values.reshape(-1,) for c in df.columns]
    columns = [c for c in df.columns]
    aligned_df = pd.DataFrame(align_dfs,index=columns).T
    #align_dfs = [d.reset_index() for d in align_dfs]
    #aligned = pd.concat([d for d in align_dfs],ignore_index=True)
    return aligned_df

@cache
def get_city_list(data, uf):
    data_filt = data.loc[(data.state.isin(uf)) & (data.place_type == "city")]
    data_filt["state_city"] = data_filt["state"] + " - " + data_filt["city"]
    return sorted(list(data_filt.state_city.drop_duplicates().values))


def _translate(country_name, names):
    if country_name in names:
        return names[country_name]
    else:
        return country_name


@cache
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


@cache
def get_countries_list(data):
    return sorted(list(data["País/Região"].drop_duplicates()))


@cache(suppress_st_warning=True)
def get_countries_data(data, countries):
    if countries:
        region_name = "País/Região"
        result = data.loc[data[region_name].isin(countries)]\
            .groupby([region_name, "Data"]).sum().reset_index()
    else:
        region_name = None
        result = data.groupby("Data").sum().reset_index()
    return region_name, result


@cache(persist=True, allow_output_mutation=True)
def load_lat_long():
    path_mapas = 'mapas/Estados.csv'
    return pd.read_csv(path_mapas)
