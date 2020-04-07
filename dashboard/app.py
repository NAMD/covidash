import streamlit as st
import pandas as pd
import numpy as np
from epimodels.continuous.models import SEQIAHR


def main():
    traces = pd.DataFrame(data=run_model())
    traces.set_index('time', inplace=True)

    st.line_chart(traces)


@st.cache
def run_model(inits=[97.3e6, 0, 1, 0, 0, 0, 0], trange=[0, 365], N=97.3e6,
              params={'chi': .3, 'phi': .01, 'beta': .5,
                      'rho': 1, 'delta': .1, 'alpha': 2,
                      'p': .75, 'q': 30
                      }):
    model = SEQIAHR()
    model(inits=inits, trange=trange, totpop=N, params={'chi': .3, 'phi': .01, 'beta': .5,
                                                        'rho': 1, 'delta': .1, 'alpha': 2,
                                                        'p': .75, 'q': 30
                                                        })
    return model.traces


@st.cache
def load_data():
    pass


if __name__ == "__main__":
    main()
