import altair as alt
import pandas as pd
import streamlit as st
from streamlit import cache
#from epimodels.continuous.models import SEQIAHR


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


def plot_model(melted_traces, q):
    lc = alt.Chart(melted_traces, width=800, height=400).mark_line().encode(
        x="time",
        y='Indivíduos',
        color='Estado',
        tooltip=['time', 'Estado', 'Indivíduos'],
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
