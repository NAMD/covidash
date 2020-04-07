import streamlit as st
import pandas as pd
import numpy as np
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


def main():
    page = st.sidebar.selectbox("Escolha um Painel", ["Home",  "Modelos", "Dados"])
    if page == "Home":
        st.header("Dashboard COVID-19")
        st.write("Escolha um painel à esquerda")
    elif page == 'Modelos':
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        chi = st.sidebar.slider('chi', 0.0, 1.0, 0.3)
        phi = st.sidebar.slider('phi', 0.0, 0.5, 0.01)
        beta = st.sidebar.slider('beta', 0.0, 1.0, 0.5)
        rho = st.sidebar.slider('rho', 0.0, 1.0, 1.0)
        delta  = st.sidebar.slider('delta', 0.0, 1.0, 0.01)
        alpha  = st.sidebar.slider('alpha', 0.0, 10.0, 2.0)
        p  = st.slider('p', 0.0, 1.0, 0.75)
        q  = st.slider('q', 0, 120, 30)
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
        pass


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
