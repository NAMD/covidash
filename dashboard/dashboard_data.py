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
        return data.loc[data.place_type == "city"].groupby("date")["Casos Confirmados"].sum()

    return data.set_index("date")


@cache
def get_city_list(data, uf):
    data_filt = data.loc[(data.state.isin(uf)) & (data.place_type == "city")]
    data_filt["state_city"] = data_filt["state"] + " - " + data_filt["city"]
    return sorted(list(data_filt.state_city.drop_duplicates().values))
