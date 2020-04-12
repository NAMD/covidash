import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from PIL import Image
from epimodels.continuous.models import SEQIAHR

import dashboard_models
import dashboard_data
from dashboard_models import seqiahr_model


st.title('A Matemática da Covid-19')

### Main menu goes here
HOME = "Home"
MODELS = "Modelos"
DATA = "Dados"
MAPA = "Distribuição Geográfica"
CREDITOS = "Equipe"
PAGE_CASE_NUMBER_BR = "Casos no Brasil"
CUM_DEATH_COUNT_BR = "Mortes acumuladas no Brasil"
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
        "Escolha uma Análise",
        [HOME, MODELS, DATA,
         PAGE_CASE_NUMBER_BR, CUM_DEATH_COUNT_BR, PAGE_GLOBAL_CASES, MAPA, CREDITOS])
    if page == HOME:
        st.header("Analizando a pandemia")
        st.markdown("""Neste site buscamos trazer até você os números da epidemia, a medida que se revelam, 
        mas também um olhar analítico, capaz de desvelar a dinâmica do processo de transmissão do vírus SARS-Cov-2
        por meio de modelos matemáticos, análises estatísticas e visualização de informação.
        
Pelo *painel à esquerda* você pode ***navegar entre nossas análises***, as quais estaremos atualizando constantemente 
daqui para frente. 
## Outros Recursos de Interesse
Vamos compilar aqui também outras fontes de informação de confiança para que você possa se manter atualizado 
com os últimos resultados científicos sobre a Pandemia.

* Canal [A Matemática das Epidemias](https://www.youtube.com/channel/UCZFllLoI5kB4o_6w59YVzAA?view_as=subscriber).
* Grupo MAVE: [Métodos Analíticos em Vigilância Epidemiológica](https://covid-19.procc.fiocruz.br).

## Fontes de Dados
As sguintes fontes de dados foram usadas neste projeto:

* [Brasil.io](https://brasil.io): Dados de incidência e mortalidade no Brasil
* [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19): Dados de incidência e mortalidade globais.

## Softwares opensource
Várias bibliotecas opensource foram utilizadas na construção deste dashboard:

* [Streamlit](streamlit.io): Web framework voltada para ciência de dados.
* [Epimodels](https://github.com/fccoelho/epimodels): Biblioteca de modelos matemáticos para simulação de epidemias.

        """)
    elif page == MODELS:
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        chi = st.sidebar.slider('χ, Fração de quarentenados', 0.0, 1.0, 0.7)
        phi = st.sidebar.slider('φ, Taxa de Hospitalização', 0.0, 0.5, 0.01)
        beta = st.sidebar.slider('β, Taxa de transmissão', 0.0, 1.0, 0.5)
        rho = st.sidebar.slider('ρ, Taxa de alta dos hospitalizados:', 0.0, 1.0, 0.02)
        delta = st.sidebar.slider('δ, Taxa de recuperação:', 0.0, 1.0, 0.1)
        alpha = st.sidebar.slider('α, Taxa de incubação', 0.0, 10.0, .33)
        mu = st.sidebar.slider('μ, Taxa de mortalidade pela COVID-19', 0.0, 1.0, .03)

        p = st.slider('Fração de assintomáticos:', 0.0, 1.0, 0.75)
        q = st.slider('Dia de início da Quarentena:', 0, 120, 50)
        r = st.slider('duração em dias da Quarentena:', 0, 200, 10)
        N = st.number_input('População em Risco:', value=97.3e6, max_value=200e6, step=1e6)
        st.markdown(f"$R_0={-(beta*chi-beta)/delta:.2f}$, durante a quarentena.")
        st.markdown(f"$R_0={-(beta * 0 - beta) / delta:.2f}$, fora da quarentena.")

        params = {
            'chi': chi,
            'phi': phi,
            'beta': beta,
            'rho': rho,
            'delta': delta,
            'alpha': alpha,
            'mu': mu,
            'p': p,
            'q': q,
            'r': r
        }
        traces = pd.DataFrame(data=seqiahr_model(params=params)).rename(columns=COLUMNS)
        final_traces = dashboard_models.prepare_model_data(traces, VARIABLES, COLUMNS, N)

        dashboard_models.plot_model(final_traces, q, r)
        st.markdown('### Formulação do modelo')
        st.write(r"""
$\frac{dS}{dt}=-\lambda[(1-\chi) S]$

$\frac{dE}{dt}= \lambda [(1-\chi) S] -\alpha E$

$\frac{dI}{dt}= (1-p)\alpha E - \delta I$

$\frac{dA}{dt}= p\alpha E -\delta A$

$\frac{dH}{dt}= \phi \delta I -(\rho+\mu) H$

$\frac{dR}{dt}= (1-\phi)\delta I +\rho H + \delta A$

$\lambda=\beta(I+A)$

$R_0 = -\frac{\beta \chi -\beta}{\delta}$
        """)

    elif page == DATA:
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
                 use_column_width=True)

    elif page == PAGE_CASE_NUMBER_BR:
        st.title(PAGE_CASE_NUMBER_BR)
        x_variable = "date"
        y_variable = "Casos Confirmados"
        data = dashboard_data.get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = dashboard_data.get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        region_name, data_uf = dashboard_data.get_data_uf(data, uf_option, city_options, y_variable)

        dashboard_data.plot_series(data_uf, x_variable, y_variable, region_name, is_log)
        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/caso)")
    elif page == CUM_DEATH_COUNT_BR:
        st.title(CUM_DEATH_COUNT_BR)
        x_variable = "date"
        y_variable = "Mortes Acumuladas"
        data = dashboard_data.get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = dashboard_data.get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        region_name, data_uf = dashboard_data.get_data_uf(
            data,
            uf_option,
            city_options,
            y_variable
        )

        dashboard_data.plot_series(data_uf, x_variable, y_variable, region_name, is_log)
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
        
        midpoint = (np.average(estados["Latitude"]), np.average(estados["Longitude"]))
                        
        geojson_url = "https://data.brasil.io/dataset/shapefiles-brasil/0.01/BR-UF.geojson"

        layer = pdk.Layer(
            "ColumnLayer",
            data=estados,
            get_position=["Longitude", "Latitude"],
            get_elevation=['casos'],
            auto_highlight=True,
            radius=50000,
            elevation_scale=300,
            get_color=[100, 255, 100, 255],
            pickable=True,
            extruded=True,
            coverage=1
        )

        view_state = pdk.ViewState(
                        longitude=midpoint[1],
                        latitude=midpoint[0],
                        zoom=3,                        
                        pitch=20.,
                        )
        
        mapbox_style = 'mapbox://styles/mapbox/light-v9'
        mapbox_key = 'pk.eyJ1IjoiZmNjb2VsaG8iLCJhIjoiY2s4c293dzc3MGJodzNmcGEweTgxdGpudyJ9.UmSRs3e4EqTOte6jYWoaxg'
        

        st.write(pdk.Deck(
            map_style=mapbox_style,
            mapbox_key=mapbox_key,
            initial_view_state=view_state,
            layers=[layer],
            tooltip={"html": "<b>Estado:</b> {Estados}<br><b>Número de casos:</b> {casos}", "style": {"color": "white"}},
        ))

        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/caso)")

    elif page == PAGE_GLOBAL_CASES:
        st.title(PAGE_GLOBAL_CASES)
        x_variable = "Data"
        y_variable = "Casos"
        global_cases = dashboard_data.get_global_cases()\
            .drop(["Province/State", "Lat", "Long"], axis="columns")

        melted_global_cases = pd.melt(
            global_cases,
            id_vars=["País/Região"],
            var_name=x_variable,
            value_name=y_variable
        )
        melted_global_cases["Data"] = pd.to_datetime(melted_global_cases["Data"])
        countries = dashboard_data.get_countries_list(melted_global_cases)
        countries_options = st.multiselect("Selecione os Países", countries)

        region_name, countries_data = dashboard_data.get_countries_data(
            melted_global_cases,
            countries_options
        )
        is_log = st.checkbox('Escala Logarítmica', value=False)

        dashboard_data.plot_series(countries_data, x_variable, y_variable, region_name, is_log)
        st.markdown("**Fonte**: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)")

    elif page == CREDITOS:
        st.markdown(open('dashboard/creditos.md', 'r').read())


if __name__ == "__main__":
    main()
