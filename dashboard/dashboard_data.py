import json

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit import cache


@cache
def get_data():
    brasil_io_url = "https://brasil.io/dataset/covid19/caso?format=csv"
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados"})
    cases["date"] = pd.to_datetime(cases["date"])

    return cases


@cache
def get_data_uf(data, uf, city_options,variable):
    if uf:
        data = data.loc[data.state.isin(uf)]
        if city_options:
            var_name = "Cidade"
            city_options = [c.split(" - ")[1] for c in city_options]
            data = data.loc[
                (data.city.isin(city_options)) & (data.place_type == "city")
            ][["date", "state", "city", variable]]
            pivot_data = data.pivot_table(values=variable, index="date", columns="city")
            data = pd.DataFrame(pivot_data.to_records())
        else:
            var_name = "Estado"
            data = data.loc[data.place_type == "state"][["date", "state", variable]]
            pivot_data = data.pivot_table(values=variable, index="date", columns="state")
            data = pd.DataFrame(pivot_data.to_records())

    else:
        var_name = "Brasil"
        data = data.loc[data.place_type == "city"].groupby("date")[variable].sum().to_frame().reset_index()

    melted_data = pd.melt(
        data,
        id_vars=['date'],
        var_name=var_name,
        value_name="Casos Confirmados"
    )
    return var_name, melted_data


def plot_series(data, var_name):
    fig = px.scatter(data, x="date", y='Casos Confirmados', color=var_name)
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
    return global_cases


@cache
def get_countries_list(data):
    return sorted(list(data["Country/Region"].drop_duplicates()))


@cache
def get_countries_data(data, countries):
    if countries:
        result = data.loc[data["Country/Region"].isin(countries)]\
            .groupby(["Country/Region", "Data"]).sum().reset_index()
        result = pd.DataFrame(
            pd.pivot_table(
                result,
                index="Data",
                columns="Country/Region",
                values="Casos").to_records()
        ).set_index("Data")
    else:
        result = data.groupby("Data").sum()
    return result


@cache(persist=True, allow_output_mutation=True)
def load_lat_long():
    path_mapas = 'mapas/Estados.csv'
    return pd.read_csv(path_mapas)
