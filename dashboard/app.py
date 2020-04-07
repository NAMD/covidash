import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from epimodels.continuous.models import SEQIAHR
st.title('Cenarios de Controle da Covid-19')


COLUMNS = {
    "A": "Asintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
}

DESCRPTION = {
    "chi": "Descrição chi",
    "phi": "Descrição phi",
    "beta": "Descrição beta",
    "rho": "Descrição rho",
    "delta": "Descrição delta",
    "alpha": "Descrição alpha",
    "p": "Descrição p",
    "q": "Descrição q",
}


def main():
    page = st.sidebar.selectbox("Escolha um Painel", ["Home",  "Modelos", "Dados"])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        st.sidebar.markdown(f"<p>&chi;<span style='color:#b2b2b2;'> {DESCRPTION['chi']}</span></p>", unsafe_allow_html=True)
        chi = st.sidebar.slider('', 0.0, 1.0, 0.3)
        st.sidebar.markdown(f"<p>&phi;<span style='color:#b2b2b2;'> {DESCRPTION['phi']}</span></p>", unsafe_allow_html=True)
        phi = st.sidebar.slider('', 0.0, 0.5, 0.01)
        st.sidebar.markdown(f"<p>&beta;<span style='color:#b2b2b2;'> {DESCRPTION['beta']}</span></p>", unsafe_allow_html=True)
        beta = st.sidebar.slider('', 0.0, 1.0, 0.5)
        st.sidebar.markdown(f"<p>&rho;<span style='color:#b2b2b2;'> {DESCRPTION['rho']}</span></p>", unsafe_allow_html=True)
        rho = st.sidebar.slider('', 0.0, 1.0, 1.0)
        st.sidebar.markdown(f"<p>&delta;<span style='color:#b2b2b2;'> {DESCRPTION['delta']}</span></p>", unsafe_allow_html=True)
        delta  = st.sidebar.slider('', 0.0, 1.0, 0.01)
        st.sidebar.markdown(f"<p>&alpha;<span style='color:#b2b2b2;'> {DESCRPTION['alpha']}</span></p>", unsafe_allow_html=True)
        alpha  = st.sidebar.slider('', 0.0, 10.0, 2.0)

        st.markdown(f"<p>p<span style='color:#b2b2b2;'> {DESCRPTION['p']}</span></p>", unsafe_allow_html=True)
        p  = st.slider('', 0.0, 1.0, 0.75)
        st.markdown(f"<p>q<span style='color:#b2b2b2;'> {DESCRPTION['q']}</span></p>", unsafe_allow_html=True)
        q  = st.slider('', 0, 120, 30)
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
        traces.set_index('time', inplace=True)

        st.line_chart(traces, height=400)
    elif page == "Dados":
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
        use_column_width=True)


@st.cache
def run_model(inits=[97.3e6, 0, 1, 0, 0, 0, 0], trange=[0, 365], N=97.3e6, params=None):
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params)
    return model.traces


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()
