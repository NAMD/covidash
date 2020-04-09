import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit import cache
from epimodels.continuous.models import SEQIAHR


@cache(suppress_st_warning=True)
def seqiahr_model(inits=None, trange=None, N=97.3e6, params=None):
    if inits is None:
        inits = [.99, 0, 1e-6, 0, 0, 0, 0]

    if trange is None:
        trange = [0, 365]

    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params)
    return model.traces


def prepare_model_data(model_data, variables, column_names, N):
    traces = pd.DataFrame(data=model_data).rename(columns=column_names)
    traces = traces[['time'] + variables]

    traces[variables] *= N #Ajusta para a escala da População em risco
    melted_traces = pd.melt(
        traces,
        id_vars=['time'],
        var_name='Estado',
        value_name="Indivíduos"
    )
    return melted_traces


def plot_model(melted_traces, q, r):
    fig = px.line(melted_traces, x="time", y="Indivíduos", color='Estado')
    fig.update_layout(
        xaxis_title="Dias",
        yaxis_title="Indivíduos",
        plot_bgcolor='rgba(0,0,0,0)',
        shapes=[
        dict(
            type= 'line',
            yref= 'paper', y0= 0, y1= 1,
            xref= 'x', x0= q, x1= q
        ),
        dict(
            type= 'line',
            yref= 'paper', y0= 0, y1= 1,
            xref= 'x', x0= q+r, x1= q+r,
            line=dict(
                color="Red",
            ),
        )
    ])
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=2, linecolor='black',
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='rgb(211,211,211)',
        showline=True, linewidth=2, linecolor='black',
    )
    st.plotly_chart(fig)
