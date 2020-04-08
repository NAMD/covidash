import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from epimodels.continuous.models import SEQIAHR

import dashboard_data
import dashboard_models
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
        model_data = dashboard_models.run_model(params=params, N=N)
        final_traces = dashboard_models.prepare_model_data(
            model_data, VARIABLES, COLUMNS, N
        )
        dashboard_models.plot_model(final_traces, q)

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


if __name__ == "__main__":
    main()
