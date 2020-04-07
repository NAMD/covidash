import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from epimodels.continuous.models import SEQIAHR
st.title('Cenarios de Controle da Covid-19')



WHOLE_BRASIL = "Brasil inteiro"
PAGE_CASE_NUMBER = "Evolução do Número de Casos"

COLUMNS = {
    "A": "Assintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
}

DESCRIPTION = {
    "chi": "Proporção da população Quarentenada",
    "phi": "Taxa de evolução para hospitalização",
    "beta": "Taxa de Transmissão",
    "rho": "Atenuação da transmissão de hospitalizados",
    "delta": "Taxa de recuperação",
    "alpha": "Taxa de incubação",
    "p": "Proporção de assintomáticos",
    "q": "Dia de início da quarentena",
    'N': "População em Risco"
}

logo = Image.open('dashboard/logo_peq.png')

def main():
    st.sidebar.image(logo, use_column_width=True)
    page = st.sidebar.selectbox("Escolha um Painel", ["Home",  "Modelos", "Dados", PAGE_CASE_NUMBER])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")

        chi = st.sidebar.slider('χ, Fração de asintomáticos', 0.0, 1.0, 0.3)

        phi = st.sidebar.slider('φ, Taxa de Hospitalização', 0.0, 0.5, 0.01)

        beta = st.sidebar.slider('β, Taxa de transmissão', 0.0, 1.0, 0.5)

        rho = st.sidebar.slider('ρ, Atenuação da Transmissão em hospitalizados:', 0.0, 1.0, 1.0)

        delta  = st.sidebar.slider('δ, Taxa de recuperação:', 0.0, 1.0, 0.01)
        alpha  = st.sidebar.slider('α, Taxa de incubação', 0.0, 10.0, 2.0)


        p  = st.slider('Fração de assintomáticos:', 0.0, 1.0, 0.75)

        q  = st.slider('Dia de início da Quarentena:', 0, 120, 30)

        N = st.number_input('População em Risco:', value=97.3e6, max_value=200e6, step=1e6)
        params = {
            'chi': chi,
            'phi': phi,
            'beta': beta,
            'rho': rho,
            'delta': delta,
            'alpha': alpha,
            'p': p,
            'q': q
        }
        traces = pd.DataFrame(data=run_model(params=params)).rename(columns=COLUMNS)
        traces = traces[['time', 'Expostos', 'Infectados', 'Assintomáticos', 'Hospitalizados', 'Hospitalizações Acumuladas']]
        traces.set_index('time', inplace=True)
        traces *= N #Ajusta para a escala da População em risco

        st.line_chart(traces, height=400)

    elif page == "Dados":
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
        use_column_width=True)

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


@st.cache(suppress_st_warning=True)
def run_model(inits=[.99, 0, 1e-6, 0, 0, 0, 0], trange=[0, 365], N=97.3e6, params=None):
    # st.write("Cache miss: model ran")
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params)
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
