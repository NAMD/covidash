import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import pydeck as pdk
from PIL import Image
from epimodels.continuous.models import SEQIAHR
import humanizer_portugues as hp

import dashboard_models
import dashboard_data
from dashboard_models import seqiahr_model

st.title('A Matemática da Covid-19')

### Main menu goes here
HOME = "Home"
MODELS = "Modelos"
DATA = "Probabilidade de Espalhamento"
MAPA = "Distribuição Geográfica"
CREDITOS = "Equipe"
PAGE_CASE_DEATH_NUMBER_BR = "Casos e Mortes no Brasil"
CUM_DEATH_CART = "Mortes registradas em cartório"
PAGE_GLOBAL_CASES = "Casos no Mundo"

COLUMNS = {
    "A": "Assintomáticos",
    "S": "Suscetíveis",
    "E": "Expostos",
    "I": "Infectados",
    "H": "Hospitalizados",
    "R": "Recuperados",
    "C": "Hospitalizações Acumuladas",
    "D": "Mortes Acumuladas",
}

VARIABLES = [
    'Expostos',
    'Infectados',
    'Assintomáticos',
    'Hospitalizados',
    'Hospitalizações Acumuladas',
    "Mortes Acumuladas"
]

logo = Image.open('dashboard/logo_peq.png')


def main():
    st.sidebar.image(logo, use_column_width=True)
    page = st.sidebar.selectbox(
        "Escolha uma Análise",
        [HOME, MODELS, DATA,
         PAGE_CASE_DEATH_NUMBER_BR, CUM_DEATH_CART, PAGE_GLOBAL_CASES, MAPA, CREDITOS])
    if page == HOME:
        st.header("Analisando a Pandemia de COVID-19 no Brasil")
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
        dashboard_data.get_data()
    elif page == MODELS:
        st.title("Explore a dinâmica da COVID-19")
        st.sidebar.markdown("### Parâmetros do modelo")
        chi = st.sidebar.slider('χ, Fração de quarentenados', 0.0, 1.0, 0.76)
        phi = st.sidebar.slider('φ, Taxa de Hospitalização', 0.0, 0.5, 0.005)
        beta = st.sidebar.slider('β, Taxa de transmissão', 0.0, 1.0, 0.6)
        rho = st.sidebar.slider('ρ, Taxa de alta dos hospitalizados:', 0.0, 1.0, 0.12)
        delta = st.sidebar.slider('δ, Taxa de recuperação de Sintomáticos:', 0.0, 1.0, 0.1)
        gamma = st.sidebar.slider('γ, Taxa de recuperação de Assintomáticos:', 0.0, 1.0, 0.05)
        alpha = st.sidebar.slider('α, Taxa de incubação', 0.0, 10.0, .37)
        mu = st.sidebar.slider('μ, Taxa de mortalidade pela COVID-19', 0.0, 1.0, .01)

        p = st.slider('Fração de assintomáticos:', 0.0, 1.0, 0.63)
        q = st.slider('Dia de início da Quarentena:', 1, 165, 35)
        r = st.slider('duração em dias da Quarentena:', 0, 200, 80)
        N = st.number_input('População em Risco:', value=102.3e6, max_value=200e6, step=1e6)
        st.markdown(f"""$R_0={-(beta * chi - beta) / delta:.2f}$, durante a quarentena. &nbsp 
                    $R_0={-(beta * 0 - beta) / delta:.2f}$, fora da quarentena.""")

        params = {
            'chi': chi,
            'phi': phi,
            'beta': beta,
            'rho': rho,
            'delta': delta,
            'gamma': gamma,
            'alpha': alpha,
            'mu': mu,
            'p': p,
            'q': q,
            'r': r
        }
        traces = pd.DataFrame(data=seqiahr_model(params=params)).rename(columns=COLUMNS)
        final_traces = dashboard_models.prepare_model_data(traces, VARIABLES, COLUMNS, N)

        # Dataframes
        Hospitalizacoes = traces['Hospitalizações Acumuladas']
        Hosp_t = traces['Hospitalizados']
        Mortes = traces['Mortes Acumuladas']
        Infectados = traces['Infectados']
        Recuperados = traces['Recuperados']

        # Valores
        pico_infectados = Infectados.iloc[Infectados.idxmax()]
        pico_hosp = Hosp_t.iloc[Hosp_t.idxmax()]
        pico_mortes = Mortes.iloc[Mortes.diff().idxmax()]
        Hospitalizacoes_totais = Hospitalizacoes.iloc[-1]
        mortes_totais = Mortes.iloc[-1]
        inf_tot = N - Recuperados.iloc[-1] - mortes_totais

        stats = pd.DataFrame(data={'Pico': [hp.intword(pico_infectados*N), hp.intword(pico_hosp*N), hp.intword(pico_mortes*N)],
                                   'Total': [hp.intword(inf_tot), hp.intword(Hospitalizacoes_totais*N), hp.intword(mortes_totais*N)]},
                             index=['Infecções', 'Hospitalizações', 'Mortes'])

        st.markdown(f"""### Números importantes da simulação""")
        st.dataframe(stats)
        st.markdown(f"""O pico das hospitalizações ocorrerá após {Hosp_t.idxmax()} dias""")
        st.markdown(f"""O pico das Mortes ocorrerá após {Mortes.diff().idxmax()} dias""")


        dashboard_models.plot_model(final_traces, q, r)
        st.markdown('''### Comparando Projeções e Dados
Podemos agora comparar nossa série simulada de Hospitalizações acumuladas com o número de casos acumulados 
de notificações oficiais.
        ''')
        ofs = st.number_input("Atraso no início da notificação (dias)", value=15, min_value=0, max_value=90, step=1)
        st.markdown('Na caixa acima, você pode mover lateralmente a curva, Assumindo que os primeiro caso '
                    'notificado não corresponde ao início da transmissão')
        dashboard_models.plot_predictions(ofs, final_traces, dias=365)
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
        st.title('Probabilidade de Epidemia por Município ao Longo do tempo')

        @st.cache
        def read_video():
            with open('dashboard/video_prob.mp4', 'rb') as v:
                video = v.read()
            return video

        st.video(read_video())
        st.markdown(r'''## Descrição da modelagem:
Os municípios brasileiros são conectados por uma malha de transporte muito bem desenvolvida e através desta,
cidadãs e cidadãos viajam diariamente entre as cidades para trabalhar, estudar e realizar outras atividades.
Considerando o fluxo de indivíduos (infectados) que chega em um município em um determinado dia, caso este município
ainda não estejam em transmissão comunitária, podemos calcular a probabilidade de uma epidemia se estabelecer.
Esta probabilidade é dada por esta fórmula:

$$P_{epi}=1-\left(\frac{1}{R_0}\right)^{I_0}$$,

onde $I_0$ é o número de infectados chegando diáriamente no município. Neste cenário usamos um $R_0=2.5$.
        ''')

    elif page == PAGE_CASE_DEATH_NUMBER_BR:
        st.title(PAGE_CASE_DEATH_NUMBER_BR)
        x_variable = "date"
        y_variable = "Casos Confirmados"
        y_variable2 = "Mortes Acumuladas"

        data = dashboard_data.get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)

        city_options = None

        if uf_option:
            cities = dashboard_data.get_city_list(data, uf_option)
            city_options = st.multiselect("Selecione os Municípios", cities)

        is_log = st.checkbox('Escala Logarítmica', value=False)
        region_name, data_uf_confirmed = dashboard_data.get_data_uf(data, uf_option, city_options, y_variable)
        region_name, data_uf_deaths = dashboard_data.get_data_uf(data, uf_option, city_options, y_variable2)

        figure = dashboard_data.plot_series(data_uf_confirmed, x_variable, y_variable, region_name, is_log)
        figure = dashboard_data.add_series(figure, data_uf_deaths, x_variable, y_variable2, region_name, is_log)

        st.plotly_chart(figure)

        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/caso)")
        st.markdown(r"""## Evolução da Mortalidade por Estado Brasileiro
No gráfico abaixo, podemos ver como a mortalidade(Fração dos casos confirmados que foi a óbito) está evoluindo 
com o tempo em cada estado.

É importante lembrar que estes números não representam todas as mortes por COVID-19 no país, pois apenas as mortes de 
casos testados e confirmados são efetivamente contadas como mortes oficiais pela COVID-19. Devido à escassez de testes e 
recomendações sobre quem deve ser testado, existe um viés nestas estimativas.

Na figura abaixo o eixo vertical representa a mortalidade: $\frac{mortes}{casos}$, o eixo Horizontal representa o número 
total de casos. O tamanho dos círculos representa o número total de mortes em cada estado. Este gráfico é mais fácil de 
ser estudado em tela cheia. clicando na legenda é possível "ligar" e "desligar" a visualização dos estados individualmente,
para facilitar a visualização dos demais. Passsndo o Mouse por sobre os circulos, podemos ler os valores da mortalidade e 
da data a que corresponde.
        """)
        dashboard_data.plot_scatter_CFR(data)

        st.markdown('''## Excesso de mortes por estado
Abaixo, exploramos o excesso de mortalidade nos estados que a COVID-19 representa, quando comparada à média dos 
últimos 10 anos de mortes por doenças respiratórias.
        ''')
        uf_option2 = st.selectbox("Selecione o Estado", ufs)
        viral = st.checkbox("Apenas Mortalidade por pneumonia viral? Desmarque para comparar com o total de mortes respiratórias", value=True)
        dashboard_data.plot_excess_deaths(data, uf_option2,viral)


    elif page == CUM_DEATH_CART:
        st.title(CUM_DEATH_CART)
        x_variable = "date"
        y_variable = "deaths_covid19"
        y_variable2 = "Mortes Acumuladas"
        data = dashboard_data.get_data_from_source(dashboard_data.BRASIL_IO_CART, usecols=None, rename_cols=None)
        data2 = dashboard_data.get_data()
        ufs = sorted(list(data.state.drop_duplicates().values))
        uf_option = st.multiselect("Selecione o Estado", ufs)
        is_log = st.checkbox('Escala Logarítmica', value=False)
        city_options = None
        # get data
        region_name, data_uf = dashboard_data.get_data_cart(data, uf_option, y_variable)
        region_name, data_uf_deaths = dashboard_data.get_data_uf(data2, uf_option, city_options, y_variable2)
        # Plota mortes dos cartorios
        fig = dashboard_data.plot_series(data_uf, x_variable, y_variable, region_name, is_log, label='Mortes registradas em Cartório')
        fig = dashboard_data.add_series(fig, data_uf_deaths, x_variable, y_variable2, region_name, is_log, "Mortes Oficiais")

        st.plotly_chart(fig)

        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/obito_cartorio)")

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
            tooltip={"html": "<b>Estado:</b> {Estados}<br><b>Número de casos:</b> {casos}",
                     "style": {"color": "white"}},
        ))

        st.markdown("**Fonte**: [brasil.io](https://brasil.io/dataset/covid19/caso)")

    elif page == PAGE_GLOBAL_CASES:
        st.title(PAGE_GLOBAL_CASES)
        x_variable = "Data"
        y_variable = "Casos"
        global_cases = dashboard_data.get_global_cases() \
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

        fig = dashboard_data.plot_series(countries_data, x_variable, y_variable, region_name, is_log)
        st.plotly_chart(fig)
        st.markdown("**Fonte**: [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)")

    elif page == CREDITOS:
        st.markdown(open('dashboard/creditos.md', 'r').read())


if __name__ == "__main__":
    main()
