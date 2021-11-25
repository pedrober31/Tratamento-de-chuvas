from numpy import object_
import pandas as pd
from calendar import monthrange
import matplotlib.pyplot as plt
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

df = pd.read_csv('/home/pedro/PycharmProjects/Projeto/Chuvas_Coruripe/chuvas_C_01036013.csv', header=8, sep=';', index_col=False, decimal=',')


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
# opcao = input('Digite o ano de chuvas que deseja visualizar: ')

# data_final_reduced.loc[opcao].plot()
# plt.show()

# classe para plotar gráfico gantt
class Plot:

    def gantt(data, monthly=True):
        """
        Make a Gantt plot, which shows the temporal data availability for each station.
        Parameters
        ----------
        data : pandas DataFrame
            A Pandas daily DataFrame with DatetimeIndex where each column corresponds to a station..
        monthly : boolean, default True
            Defines if the availability count of the data will be monthly to obtain a more fluid graph.
        Returns
        -------
        fig : plotly Figure
        """

        date_index = pd.date_range(data.index[0], data.index[-1], freq='D')
        data = data.reindex(date_index)
        periods = []
        for column in data.columns:
            series = data[column]
            if monthly:
                missing = series.isnull().groupby(pd.Grouper(freq='1MS')).sum().to_frame()
                series_drop = missing.loc[missing[column] < 7]  # A MONTH WITHOUT 7 DATA IS CONSIDERED A MISSING MONTH
                DELTA = 'M'
            else:
                series_drop = series.dropna()
                DELTA = 'D'
            if series_drop.shape[0] > 1:
                task = column
                resource = 'Available data'
                start = str(series_drop.index[0].year) + '-' + str(series_drop.index[0].month) + '-' + str(
                    series_drop.index[0].day)
                finish = 0
                for i in range(len(series_drop)):
                    if i != 0 and round((series_drop.index[i] - series_drop.index[i - 1]) / np.timedelta64(1, DELTA),
                                        0) != 1:
                        finish = str(series_drop.index[i - 1].year) + '-' + str(
                            series_drop.index[i - 1].month) + '-' + str(
                            series_drop.index[i - 1].day)
                        periods.append(dict(Task=task, Start=start, Finish=finish, Resource=resource))
                        start = str(series_drop.index[i].year) + '-' + str(series_drop.index[i].month) + '-' + str(
                            series_drop.index[i].day)
                        finish = 0
                finish = str(series_drop.index[-1].year) + '-' + str(series_drop.index[-1].month) + '-' + str(
                    series_drop.index[-1].day)
                periods.append(dict(Task=task, Start=start, Finish=finish, Resource=resource))
            else:
                print('Station {} has no months with significant data'.format(column))
        periods = pd.DataFrame(periods)
        start_year = periods['Start'].apply(lambda x: int(x[:4])).min()
        finish_year = periods['Start'].apply(lambda x: int(x[:4])).max()
        colors = {'Available data': 'rgb(0,191,255)'}
        fig = ff.create_gantt(periods, colors=colors, index_col='Resource', show_colorbar=True, showgrid_x=True,
                              showgrid_y=True, group_tasks=True)

        fig.layout.xaxis.tickvals = pd.date_range('1/1/' + str(start_year), '12/31/' + str(finish_year + 1), freq='2AS')
        fig.layout.xaxis.ticktext = pd.date_range('1/1/' + str(start_year), '12/31/' + str(finish_year + 1),
                                                  freq='2AS').year
        return fig



# Construção do gráfico de gantt
def gantt_chart(df):
    
    # Disponibilidade de dados:
    gantt_fig = Plot.gantt(df)
    
    #Atualizando o layout da figura
    gantt_fig.update_layout(
        autosize=False,
        width=1200, #Determina a largura da figura em pixels
        height=1000, #Determina a altura da figura em pixels
        xaxis_title = 'Ano', #Título do eixo 
        yaxis_title = 'Código da Estação', #Título do eixo y.
        font=dict(family="Courier New, monospace", size=12))
    
    #Plotando
    plot(gantt_fig)
    return gantt_fig


gantt_chart(data_final_reduced)
