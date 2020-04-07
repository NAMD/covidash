import streamlit as st
import pandas as pd
import numpy as np
from epimodels.continuous.models import SEQIAHR
st.title('Cenarios de Controle da Covid-19')


WHOLE_BRASIL = "Brasil inteiro"
PAGE_CASE_NUMBER = "Evolução do Número de Casos"


def main():
    page = st.sidebar.selectbox("Escolha um Painel", ["Home",  "Modelos", "Dados", PAGE_CASE_NUMBER])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        traces = pd.DataFrame(data=run_model())
        traces.set_index('time', inplace=True)

        st.line_chart(traces)

    elif page == "Dados":
        pass

    elif page == PAGE_CASE_NUMBER:
        st.title("Casos Confirmados no Brasil")
        data = get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.selectbox("Selecione o Estado", [WHOLE_BRASIL] + ufs)

        city_option = None
        if uf_option != WHOLE_BRASIL:
            cities = get_city_list(data, uf_option)
            city_option = st.selectbox("Selecione o Município", ["Todos"] + cities)

        data_uf = get_data_uf(data, uf_option, city_option)

        st.line_chart(data_uf, height=400)


@st.cache
def run_model(inits=[97.3e6, 0, 1, 0, 0, 0, 0], trange=[0, 365], N=97.3e6,
              params={'chi': .3, 'phi': .01, 'beta': .5,
                      'rho': 1, 'delta': .1, 'alpha': 2,
                      'p': .75, 'q': 30
                      }):
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params={'chi': .3, 'phi': .01, 'beta': .5,
                                                        'rho': 1, 'delta': .1, 'alpha': 2,
                                                        'p': .75, 'q': 30
                                                        })
    return model.traces

@st.cache
def get_data():
    brasil_io_url = "https://brasil.io/dataset/covid19/caso?format=csv"
    cases = pd.read_csv(brasil_io_url).rename(
        columns={"confirmed": "Casos Confirmados"})

    return cases


@st.cache
def get_data_uf(data, uf, city_option):
    if uf != WHOLE_BRASIL:
        data = data.loc[data.state == uf]
        if city_option and city_option != "Todos":
            data = data.loc[data.city == city_option]

    return data.groupby("date")["Casos Confirmados"].sum()


@st.cache
def get_city_list(data, uf):
    return sorted(list(data.loc[(data.state==uf) & (~data.city.isnull())].city.drop_duplicates()))


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()
