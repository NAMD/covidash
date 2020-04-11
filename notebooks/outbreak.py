# -*- coding: utf-8 -*-
import networkx as nx
import pandas as pd
import numpy as np
import dask.array as da
#import dask.dataframe as dd
import geopandas as gpd
import contextily as ctx
from scipy.special import lambertw
import pylab as P


def read_flow_matrix(fname, header=0):
    """
    Read flow matrix from csv with or without headers
    For CSV without header use header=None
    """
    df = pd.read_csv(fname, header=header)
    return df.values


def read_nodes(fname):
    '''
    Reads csv with MR names geocodes, populations and Incidences
    '''
    nodes = pd.read_csv(fname)
    return nodes


def plot_probs(nodes, probs, mapa, figsize=(10, 10), geocfield='CD_GEOCMI', nodes_geocfield='geoc', basemap=True,nat_breaks=False):
    '''
    Plots map colored with the probability of epidemics.

    '''
    mapa[geocfield] = mapa[geocfield].astype(int)

    nodes['probs'] = probs
    mapa = pd.merge(mapa, nodes, left_on=geocfield, right_on=nodes_geocfield)
    fig, ax = P.subplots(1, 1, figsize=figsize)
    mapa = mapa.to_crs(epsg=3857)
    # print(mapa.columns)
    if nat_breaks:
        mapa.plot(ax=ax, column='probs', alpha=1, legend=True, 
                  scheme='user_defined', classification_kwds={'bins':[0, .5, .8, 1]}
                 )
    else:
        mapa.plot(ax=ax, column='probs', alpha=1, legend=True)
    if basemap:
        ctx.add_basemap(ax)
    ax.set_axis_off()
    return mapa


def get_outbreaks(flowmat, incidence, R0=2.5, asymf=10, attenuate=1.0):
    """
    Calculate the probabilities of outbreak for all regions

    :param flowmat: Arriving passengers row -> column
    :param incidence: fraction of infectious in the populations
    :param R0: Basic reproduction number
    :param asymf: how many asymptomatics per reported case
    :param attenuate: Attenuation factor for flow
    :return:
    """
    # Adjusting arrivals by incidence

    inflows = (flowmat.T * attenuate) @ incidence

    probs = 1 - (1 / R0) ** (inflows * 8 * asymf)

    return probs


def calc_epi_size(nodes, R0=2.5):
    '''
    Calculate final epidemic size based on the SIR Model
    Formula.
    '''
    I0 = nodes['I'].values
    N = nodes['pop'].values
    S0 = N - I0
    S_inf = -(N*lambertw(-(R0*S0*np.exp(-(R0*(I0+S0))/N))/N))/R0
    return N - S_inf

def calc_peak_size(nodes, R0=2.5):
    '''
    Calculate the peak size
    '''
    I0 = nodes['I'].values
    N = nodes['pop'].values
    S0 = N - I0
    Imax = N*(1- (1 + np.log(R0))/R0)
    nodes['peak_size'] = Imax
    nodes['frac_prev'] = Imax/N
    return nodes



def plot_ranking(nodes, probs, figsize=(10, 10), namefield='nome'):
    '''
    Creates a horizontal bar plot with ranking of MRs
    by probability of epidemic.
    '''
    ranking = pd.DataFrame(data={'Microrregião': nodes[namefield], 'Probabilidade': probs})
    ranking.set_index('Microrregião', inplace=True)
    ranking.sort_values('Probabilidade', ascending=True, inplace=True)
    fig, ax = P.subplots(1, 1, figsize=figsize)
    ranking.tail(20).plot.barh(ax=ax)
    return ranking


if __name__ == "__main__":
    F = read_flow_matrix('flowmatrix_full.csv', header=None)
    nodes = read_nodes('../Dados/nodes.csv')
    mapa = gpd.read_file('microreg.gpkg')
    nodes['incidence'] = (nodes.I / nodes['pop'])

    probs = get_outbreaks(F, nodes.incidence)
    plot_probs(nodes, probs, mapa)
    ranking = plot_ranking(nodes, probs)
    P.show()
