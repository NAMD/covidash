import pandas as pd
import numpy as np
import datetime
from pysus.online_data.SIM import download
from pysus.online_data import cache_contents
from pysus.preprocessing.decoders import decodifica_idade_SIM
from concurrent.futures import ThreadPoolExecutor
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import episem
import matplotlib
from functools import lru_cache
import os

YEARS = range(2009, 2019)
### data sources
BRASIL_IO_COVID19 = "https://brasil.io/dataset/covid19/caso?format=csv"
BRASIL_IO_CART = "https://brasil.io/dataset/covid19/obito_cartorio?format=csv"

@lru_cache(maxsize=1)
def fetch_brasilio_data():
    cases = pd.read_csv(BRASIL_IO_COVID19)
    cases = cases[cases.place_type=='state']
    return cases


def download_SIM(ano, estado):
    '''
    Download and saves on PySUS cache directory
    :param ano:
    :param estado:
    :return:
    '''
    download(estado, ano)


def get_data_from_cart(source, usecols=None, rename_cols=None):
    df = pd.read_csv(source, usecols=usecols)
    if rename_cols:
        df.rename(columns=rename_cols)
    df["date"] = pd.to_datetime(df["date"])
    return df


def get_data_cart_uf(data, uf, variable):
    if uf:
        data = data.loc[data.state.isin(uf)]
        region_name = "Estado"
        data = data.loc[:, ["date", "state", variable]]
        pivot_data = data.pivot_table(values=variable, index="date", columns="state")
        data = pd.DataFrame(pivot_data.to_records())
    else:
        region_name = "Brasil"
        data = data.groupby("date")[variable].sum().to_frame().reset_index()

    melted_data = pd.melt(
        data,
        id_vars=['date'],
        var_name=region_name,
        value_name=variable,
    )
    return region_name, melted_data


def converte_datas(df):
    for c in df.columns:
        if c.startswith('DT'):
            df[c] = pd.to_datetime(df[c], format='%d%m%Y', errors='coerce')
    return df


def load_anos(estado):
    '''
    Lê dados do SIM diretamente do Cache.
    Todos os anos disponíveis para o Estado
    '''
    cols2read = ['NUMERODO', 'CODMUNOCOR', 'DTOBITO', 'CAUSABAS', 'IDADE', 'SEXO', 'LINHAA', 'LINHAB']
    anos = []
    for fi in cache_contents():
        if (f'SIM_DO{estado}' in fi):
            print("Loading ", fi)
            df = pd.read_parquet(fi, engine='pyarrow', columns=cols2read)
            df = converte_datas(df)
            df['idade'] = df.IDADE.apply(lambda x: decodifica_idade_SIM(x))
            df.set_index('DTOBITO', inplace=True)
            anos.append(df)
    #     print(meses)
    ddf = pd.concat(anos)
    return ddf


def plot_obitos_covid(estado, cases):
    obitos = filtra_obitos_covid(cases, estado)
    ax = obitos.incidencia.resample('W').sum().plot(style='r:+', figsize=(20, 8), grid=True)
    ax.set_title(f'Óbitos por semana para {estado}')
    obitos.to_csv(f'obitos_covid_{estado}.csv.gz')
    # ~ plt.show()
    return obitos


def filtra_obitos_covid(cases, estado):
    obitos = cases[(cases.state == estado) & (cases.place_type == 'state')][['date', 'confirmed', 'deaths']]
    obitos['data'] = pd.to_datetime(obitos.date)
    obitos.set_index('data', inplace=True)
    obitos.sort_index(inplace=True)
    obitos['incidencia'] = obitos.deaths.diff()
    obitos['ew'] = [int(episem.episem(x, out='W')) for x in obitos.index]
    return obitos


def plot_serie_SIM(estado):
    pneu_obitos = filtra_obitos_SIM(estado)
    ax = pneu_obitos.CAUSABAS.resample('W').count().plot(style='b:o', rot=45, figsize=(20, 5), grid=True,
                                                         label='Baseline');
    return


def filtra_obitos_SIM(estado, only_viral=True):
    df = load_anos(estado)
    if only_viral:
        pneu = ['J09', 'J090', 'J100', 'J108', 'J110', 'J111', 'J118', 'J120', 'J121', 'J122', 'J128', 'J129', 'J171']
    else:
        pneu = set([cid for cid in df.CAUSABAS if cid.startswith('J1')]+['J09', 'J090'])
    pneu_obitos = df[df.CAUSABAS.isin(pneu) | df.LINHAA.isin(pneu) | df.LINHAB.isin(pneu)]
    return pneu_obitos

def df_baseline_estado(estado, viral=True):
    pneu_obitos = filtra_obitos_SIM(estado, only_viral=viral)
    avg = pneu_obitos.resample('W').count()
    avg['week'] = avg.index.week
    median = avg.groupby('week').median()
    new_df = median.drop(['CODMUNOCOR','IDADE','SEXO','LINHAA','LINHAB','idade'], axis=1)
    new_df = new_df.rename(columns={"CAUSABAS": "median"})
    new_df['perc_75'] = avg.groupby('week').agg(lambda x: np.percentile(x, 75)).CAUSABAS
    new_df['perc_25'] = avg.groupby('week').agg(lambda x: np.percentile(x, 25)).CAUSABAS
    return new_df

def plot_baseline_estado(estado):
    pneu_obitos = filtra_obitos_SIM(estado)
    avg = pneu_obitos.resample('W').count()
    avg['week'] = avg.index.week
    ax = avg.groupby('week').median().CAUSABAS.plot(style='-o', figsize=(20, 5), grid=True, label='Median')
    avg.groupby('week').agg(lambda x: np.percentile(x, 75)).CAUSABAS.plot(ax=ax, style=':', figsize=(20, 5), grid=True,
                                                                          label='75%')
    avg.groupby('week').agg(lambda x: np.percentile(x, 25)).CAUSABAS.plot(ax=ax, style=':', figsize=(20, 5), grid=True,
                                                                          label='25%')
    obitos = filtra_obitos_covid(data_covid, estado)
    obitos.groupby('ew').sum().incidencia.iloc[:-1].plot(ax=ax, style='r:+', figsize=(20, 8), grid=True, logy=False);
    ax.set_title(f'Esperado Histórico para {estado}')
    ax.legend()
    plt.show()


if __name__ == "__main__":
    data_covid = fetch_brasilio_data()
    estados = set(data_covid.state)
    viral = False
    ## Preenchendo o Cache
    ## Rode apenas uma vez
    if not os.path.exists('baseline'):
        os.makedirs('baseline')

    for est in estados:
        if os.path.exists(f'baseline/baseline_{est}.csv'):
            continue
        print(f"Baixando {est}...")
        for ano in YEARS:
            download_SIM(ano, est)
        base = df_baseline_estado(est, viral=viral)
        if viral:
            base.to_csv(f'baseline/baseline_{est}.csv.gz')  
        else:
            base.to_csv(f'baseline/baseline_{est}_all_resp.csv.gz')
        # ~ plot_obitos_covid(est, data_covid)  
        
    excesso = pd.DataFrame(columns=['estado','mediana_historica', 'covid','diferença'])

    # ~ for est in estados:
        # ~ print(f'plotando {est}')
        # ~ obitos = plot_obitos_covid(est, data_covid)
        # ~ bldf = pd.read_csv(f'baseline/baseline_{est}.csv.gz')
        # ~ last_week = obitos.groupby('ew').sum().incidencia.iloc[-1]
        # ~ base = bldf['median'].iloc[obitos.ew.iloc[-1]]
        # ~ excesso = excesso.append({'estado': est,
                        # ~ 'mediana_historica': int(base),
                        # ~ 'covid':int(last_week),
                        # ~ 'diferença':int(last_week-base)
                    # ~ },ignore_index=True)
                    
    #    plot_baseline_estado(est)
    # ~ excesso.to_csv(f'Excesso_mortes_semana_{obitos.ew.iloc[-1]}.csv')
