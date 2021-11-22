from numpy import object_
import pandas as pd
from calendar import monthrange
import matplotlib.pyplot as plt

df = pd.read_csv('Chuvas_Coruripe/chuvas_C_01036013.csv', header=8, sep=';', index_col=False, decimal=',')


def dados_chuvas(dataframe):
    df1 = dataframe.copy()
    dados = df1.iloc[:, 13:44]
    dados = pd.concat([df1['Data'], df1['NivelConsistencia'], dados], axis=1)
    dados = dados.sort_index(ascending=False).reset_index()
    dados = dados.drop(columns='index')
    dados['Data'] = pd.to_datetime(dados['Data'], dayfirst=True) 
    dados = dados.set_index(['Data', 'NivelConsistencia'])
    return dados


data_rain = dados_chuvas(df)


def organize_data_rain(dataframe_rain):
    df_general = pd.DataFrame()
    for p in dataframe_rain.index:
        num_days = monthrange(p[0].year, p[0].month)[1]
        date = pd.date_range(start=p[0], periods=num_days, freq='D')
        data = dataframe_rain.loc[p][:num_days].values
        list_consistence = [p[1]] * num_days
        dicio = {'date': date, 'data': data, 'consistency': list_consistence}
        df2 = pd.DataFrame(dicio)
        df2 = df2.set_index(['date', 'consistency'])
        df_general = df_general.append(df2)
        df_general = pd.concat([df_general])
    return df_general


data_final = organize_data_rain(data_rain)

# Criação do dataframe para visulização dos gráficos
data_final_reduced = data_final.copy()
data_final_reduced = data_final_reduced.reset_index()
data_final_reduced = data_final_reduced.drop(columns='consistency')
data_final_reduced = data_final_reduced.set_index('date')

# Vizulização dos gráficos
opcao = input('Digite o ano de chuvas que deseja visualizar: ')

data_final_reduced.loc[opcao].plot()
plt.show()
