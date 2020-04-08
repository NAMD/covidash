import streamlit as st
from epimodels.continuous.models import SEQIAHR

@st.cache(suppress_st_warning=True)
def seqiahr_model(inits=[.99, 0, 1e-6, 0, 0, 0, 0], trange=[0, 365], N=97.3e6, params=None):
    # st.write("Cache miss: model ran")
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params=params)
    return model.traces