import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from epimodels.continuous.models import SEQIAHR
import dashboard_models
import dashboard_data
from dashboard_models import seqiahr_model
import pydeck as pdk
import altair as alt

st.title('Cenarios de Controle da Covid-19')

MAPA = "Distribuição Geográfica"
CREDITOS = "Equipe"
PAGE_CASE_NUMBER = "Casos no Brasil"
PAGE_GLOBAL_CASES = "Casos no Mundo"

COLUMNS = {
    "A": "Assintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
}

VARIABLES = [
    'Expostos',
    'Infectados',
    'Assintomáticos',
    'Hospitalizados',
    'Hospitalizações Acumuladas'
]

logo = Image.open('dashboard/logo_peq.png')


def main():
    st.sidebar.image(logo, use_column_width=True)
    page = st.sidebar.selectbox(
        "Escolha um Painel",
        ["Home", "Modelos", "Dados",
         PAGE_CASE_NUMBER, PAGE_GLOBAL_CASES, MAPA, CREDITOS])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        chi = st.sidebar.slider('χ, Fração de quarentenados', 0.0, 1.0, 0.3)
        phi = st.sidebar.slider('φ, Taxa de Hospitalização', 0.0, 0.5, 0.01)
        beta = st.sidebar.slider('β, Taxa de transmissão', 0.0, 1.0, 0.5)
        rho = st.sidebar.slider('ρ, Atenuação da Transmissão em hospitalizados:', 0.0, 1.0, 1.0)
        delta = st.sidebar.slider('δ, Taxa de recuperação:', 0.0, 1.0, 0.01)
        alpha = st.sidebar.slider('α, Taxa de incubação', 0.0, 10.0, 2.0)

        p = st.slider('Fração de assintomáticos:', 0.0, 1.0, 0.75)
        q = st.slider('Dia de início da Quarentena:', 0, 120, 30)
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
        traces = pd.DataFrame(data=seqiahr_model(params=params)).rename(columns=COLUMNS)
        final_traces = dashboard_models.prepare_model_data(traces, VARIABLES, COLUMNS, N)

        dashboard_models.plot_model(final_traces, q)
        st.markdown('### Formulação do modelo')
        st.write(r"""
$\frac{dS}{dt}=-\lambda[(1-\chi) S]$

$\frac{dE}{dt}= \lambda [(1-\chi) S] -\alpha E$

$\frac{dI}{dt}= (1-p)\alpha E - (\phi+\delta)I$

$\frac{dA}{dt}= p\alpha E -\delta A$

$\frac{dH}{dt}= \phi I -\delta H$

$\frac{dR}{dt}= \delta I +\delta H + \delta A$

$\lambda=\beta(I+A+(1-\rho)H)$
        """)

    elif page == "Dados":
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
                 use_column_width=True)

    elif page == PAGE_CASE_NUMBER:
        st.title("Casos Confirmados no Brasil")
        data = dashboard_data.get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = dashboard_data.get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        data_uf = dashboard_data.get_data_uf(data, uf_option, city_options)
        data_uf = np.log(data_uf + 1) if is_log else data_uf

        st.line_chart(data_uf, height=400)
        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/caso)")

    elif page == MAPA:

        # Precisa refatorar
        st.title("Distribuição Geográfica de Casos")
        cases = dashboard_data.get_data()
        estados = dashboard_data.load_lat_long()
        estados['casos'] = 0
        cases = cases[cases.place_type != 'state'].groupby(['date', 'state']).sum()
        cases.reset_index(inplace=True)

        for i, row in estados.iterrows():
            if row.Estados in list(cases.state):
                estados.loc[estados.Estados == row.Estados, 'casos'] += \
                cases[(cases.state == row.Estados) & (cases.is_last)]['Casos Confirmados'].iloc[0]

        estados = estados.set_index('Estados')
        midpoint = (np.average(estados["Latitude"]), np.average(estados["Longitude"]))

        layer = pdk.Layer(
            "HexagonLayer",
            data=estados,
            get_position=["Longitude", "Latitude"],
            radius=1000,
            elevation_scale=10,
            elevation_range=[0, 2000],
            pickable=True,
            extruded=True,
        )

        st.write(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            mapbox_key='pk.eyJ1IjoiZmNjb2VsaG8iLCJhIjoiY2s4c293dzc3MGJodzNmcGEweTgxdGpudyJ9.UmSRs3e4EqTOte6jYWoaxg',
            initial_view_state={
                "latitude": midpoint[0],
                "longitude": midpoint[1],
                "zoom": 3,
                "pitch": 20,
            },
            layers=[layer]
            ,
        ))

    elif page == PAGE_GLOBAL_CASES:
        global_cases = dashboard_data.get_global_cases()\
            .drop(["Province/State", "Lat", "Long"], axis="columns")
        melted_global_cases = pd.melt(
            global_cases,
            id_vars=["Country/Region"],
            var_name="Data",
            value_name="Casos"
        )
        melted_global_cases["Data"] = pd.to_datetime(melted_global_cases["Data"])
        countries = dashboard_data.get_countries_list(melted_global_cases)
        countries_options = st.multiselect("Selecione os Países", countries)

        countries_data = dashboard_data.get_countries_data(
            melted_global_cases,
            countries_options
        )
        is_log = st.checkbox('Escala Logarítmica', value=False)
        countries_data = np.log(countries_data + 1) if is_log else countries_data
        st.line_chart(countries_data, height=400)
        st.markdown("**Fonte**: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)")

    elif page == CREDITOS:
        st.markdown('''# Equipe do Dashboard
        Este é um esforço voluntário de várias pessoas. Saiba mais sobre nós:
        ''')


if __name__ == "__main__":
    main()
