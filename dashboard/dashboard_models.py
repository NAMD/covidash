import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import timedelta
import matplotlib.pyplot as plt

from epimodels.continuous.models import SEQIAHR
import dashboard_data
import settings


@st.cache(suppress_st_warning=True, ttl=settings.CACHE_TTL)
def seqiahr_model(inits=None, trange=None, N=97.3e6, params=None):
    if inits is None:
        inits = [.99, 0, 1e-6, 0, 0, 0, 0, 0]

    if trange is None:
        trange = [0, 365]

    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params, t_eval=range(*trange))
    return model.traces


def prepare_model_data(model_data, variables, column_names, N):
    traces = pd.DataFrame(data=model_data).rename(columns=column_names)
    traces = traces[['time'] + variables]

    traces[variables] *= N  # Ajusta para a escala da População em risco
    melted_traces = pd.melt(
        traces,
        id_vars=['time'],
        var_name='Estado',
        value_name="Indivíduos"
    )
    return melted_traces


def plot_model(melted_traces, q, r):
    fig = px.line(melted_traces, x="time", y="Indivíduos", color='Estado', height=500)
    fig.update_layout(
        xaxis_title="Dias",
        yaxis_title="Indivíduos",
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend_title="",
        legend=dict(
            y=-0.15,
        ),
        shapes=[
            dict(
                type='line',
                yref='paper', y0=0, y1=1,
                xref='x', x0=q, x1=q
            ),
            dict(
                type='line',
                yref='paper', y0=0, y1=1,
                xref='x', x0=q + r, x1=q + r,
                line=dict(
                    color="Red",
                ),
            ),
            dict(type='rect',
                 yref='paper', y0=0, y1=1,
                 ysizemode='scaled',
                 xref='x', x0=q, x1=q + r,
                 opacity=0.3,
                 fillcolor='gray',
                 ),
        ])
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=1, linecolor='black',
    )

    # data = dashboard_data.get_data()
    # region_name, data_uf = dashboard_data.get_data_uf(data, False, [], "Casos Confirmados")
    # fig2 = px.line(melted_traces[melted_traces.Estado=='Hospitalizados'],
    #                x="time", y="Indivíduos", color='Estado', height=500)
    # fig2.update_layout(
    #     xaxis_title="Dias",
    #     yaxis_title="Indivíduos",
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     legend_orientation="h",
    #     legend_title="",
    #     legend=dict(
    #         y=-0.15,
    #     )
    # )
    # fig2.add_trace(px.scatter(data_uf, x=data.index, y="Casos Confirmados", color=region_name))
    st.plotly_chart(fig)
    # st.plotly_chart(fig2)


def plot_predictions(offset, melted_traces, dias=365):
    htrace = melted_traces[melted_traces.Estado == 'Hospitalizações Acumuladas']
    mtrace = melted_traces[melted_traces.Estado == 'Mortes Acumuladas']
    htrace.loc[:, 'dtime'] = htrace.time.astype(int)
    mtrace.loc[:, 'dtime'] = mtrace.time.astype(int)
    htrace = htrace.groupby('dtime').mean()
    mtrace = mtrace.groupby('dtime').mean()

    data = dashboard_data.get_data()
    region_name, data_uf = dashboard_data.get_data_uf(data, False, [], "Casos Confirmados")
    region_name, m_data_uf = dashboard_data.get_data_uf(data, False, [], "Mortes Acumuladas")
    drange = pd.date_range(data_uf[data_uf['Casos Confirmados'] > 0].date.min() - timedelta(offset),
                           periods=dias,
                           freq='D')
    fig, ax = plt.subplots(1, 1)
    ax.semilogy(drange, htrace['Indivíduos'].values, '-v', label='Casos previstos')
    ax.semilogy(drange, mtrace['Indivíduos'].values, '-v', label='Mortes previstas')
    data_uf.loc[:, 'date2'] = data_uf.date
    data_uf.set_index('date2', inplace=True)
    data_uf[data_uf['Casos Confirmados'] > 0]['Casos Confirmados'].plot(ax=ax, style='o',
                                                                        label='Dados oficiais',
                                                                        grid=True,
                                                                        logy=True)
    m_data_uf.loc[:, 'date2'] = m_data_uf.date
    m_data_uf.set_index('date2', inplace=True)

    m_data_uf[m_data_uf['Mortes Acumuladas'] > 0]['Mortes Acumuladas'].plot(ax=ax, style='o',
                                                                        label='Mortes oficiais',
                                                                        grid=True,
                                                                        logy=True)
    ax.set_xlabel('Data (dias)')
    ax.set_ylabel('Casos acumulados')
    plt.legend()
    st.pyplot()
