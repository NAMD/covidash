import pandas as pd
from streamlit import cache


@cache
def get_data():
    brasil_io_url = "https://brasil.io/dataset/covid19/caso?format=csv"
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados"})

    return cases


@cache
def get_data_uf(data, uf, city_options):
    if uf:
        data = data.loc[data.state.isin(uf)]
        if city_options:
            city_options = [c.split(" - ")[1] for c in city_options]
            data = data.loc[
                (data.city.isin(city_options)) & (data.place_type == "city")
            ][["date", "state", "city", "Casos Confirmados"]]
            pivot_data = data.pivot_table(values="Casos Confirmados", index="date", columns="city")
            data = pd.DataFrame(pivot_data.to_records())
        else:
            data = data.loc[data.place_type == "state"][["date", "state", "Casos Confirmados"]]
            pivot_data = data.pivot_table(values="Casos Confirmados", index="date", columns="state")
            data = pd.DataFrame(pivot_data.to_records())

    else:
        return data.loc[data.place_type == "city"].groupby("date")["Casos Confirmados"].sum().to_frame()

    return data.set_index("date")

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


@cache
def get_global_cases():
    url = (
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
        "csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_"
        "confirmed_global.csv"
    )
    return pd.read_csv(url)


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
