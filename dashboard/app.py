import altair as alt
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
        traces = pd.DataFrame(data=run_model(params=params)).rename(columns=COLUMNS)
        traces = traces[['time'] + VARIABLES]
        #traces.set_index('time', inplace=True)
        traces[VARIABLES] *= N #Ajusta para a escala da População em risco
        melted_traces = pd.melt(
            traces,
            id_vars=['time'],
            var_name='Grupos',
            value_name="Número de Casos Estimados"
        )
        plot_model(melted_traces, q)

    elif page == "Dados":
        st.title('Probabilidade de Epidemia por Município')
        probmap = Image.open('dashboard/Outbreak_probability_full_mun_2020-04-06.png')
        st.image(probmap, caption='Probabilidade de Epidemia em 6 de abril',
        use_column_width=True)

    elif page == PAGE_CASE_NUMBER:
        st.title("Casos Confirmados no Brasil")
        data = get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None
        if uf_option:
            cities = get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        data_uf = get_data_uf(data, uf_option, city_options)
        data_uf = np.log(data_uf + 1) if is_log else data_uf

        st.line_chart(data_uf, height=400)


def plot_model(melted_traces, q):
    lc = alt.Chart(melted_traces, width=800, height=400).mark_line().encode(
        x="time",
        y='Número de Casos Estimados',
        color='Grupos',
    ).encode(
        x=alt.X('time', axis=alt.Axis(title='Dias'))
    )
    vertline = alt.Chart().mark_rule(strokeWidth=2).encode(
        x='a:Q',
    )
    la = alt.layer(
        lc, vertline,
        data=melted_traces
    ).transform_calculate(
        a="%d" % q
    )
    st.altair_chart(la)


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


@st.cache
def get_city_list(data, uf):
    data_filt = data.loc[(data.state.isin(uf)) & (data.place_type == "city")]
    data_filt["state_city"] = data_filt["state"] + " - " + data_filt["city"]
    return sorted(list(data_filt.state_city.drop_duplicates().values))


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()
