from stations import Flow, estacoes_nao_afetadas
import pandas as pd
import numpy as np
import math

caminho_ottobacias = r"C:\Users\pedro\Documents\Pibic\ach_2017_5k\ach_2017_5k.shp"
caminho_reservatorios = r"C:\Users\pedro\Documents\Pibic\Reservatorios_do_Semiarido_Brasileiro\Reservatorios_do_Semiarido_Brasileiro.shp"
estacoes_nafetadas = estacoes_nao_afetadas(caminho_ottobacias, caminho_reservatorios, 1421, 2)

lista_estacoes = estacoes_nafetadas['Code'].to_list()
flow = Flow(lista_estacoes)
df1 = flow.track_back()
df2 = flow.data()

class Hydro_Sig():

    def __init__(self, station):
        self.station = station
    
    def skew(self, data=df2):
        mean = data[self.station].mean()
        median = data[self.station].median()
        return mean / median

    def qsp(self):
        media = df2[self.station].mean()
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        return media / drainage_area

    def cvq(self, data=df2):
        cv = data[self.station].std() / data[self.station].mean()
        return cv

    def bfi(self, data=df2):
        return data[self.station].rolling(7).mean().min() / data[self.station].mean()

    def q5(self, data=df2):
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        ef = data[self.station] / drainage_area.values[0]
        return ef.quantile(q=0.95)

    def hfd(self):
        return df2[self.station].quantile(q=0.9) / df2[self.station].mean()

    def q95(self, data=df2):
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        ef = data[self.station] / drainage_area.values[0]
        return ef.quantile(q=0.05)

    def lowfr(self):
        lim = df2[self.station].mean() * 0.05
        res = len(df2[self.station][df2[self.station] < lim]) / len(df2[self.station].dropna())
        return res

    def highfrvar(self):
        q75 = df2[self.station].quantile(q=.25)
        res = df2[self.station][df2[self.station] > q75].std() / df2[self.station][df2[self.station] > q75].mean()
        return res
    
    def hidrological_year(self):
        vaz_mensal = df2[self.station].groupby(pd.Grouper(freq='M')).mean()

        for ano in vaz_mensal.index.year:
            if vaz_mensal[f"{ano}"].count() == 12:
                ano_analisado = ano
                break
            elif 6 <= vaz_mensal[f"{ano}"].count() < 12:
                ano_analisado = ano
                break
        
        vaz_interesse = vaz_mensal[f"{ano_analisado}"]
        valor_min = vaz_interesse.min()
        mes_inicio = vaz_interesse[vaz_interesse == valor_min].index.month[0]
        return mes_inicio

    def constancy(self):
        o_station = Hydro_Sig(self.station)

        mes = o_station.hidrological_year()

        df_const = pd.DataFrame(index=['Skew', 'CVQ', 'BFI', 'Q5', 'Q95'], columns=list(set(df2.index.year))[:-1])

        for y in df_const.columns:

            if mes == 1:
                df_a = df2.loc[f'{y}']
            else:
                df_a = df2.loc[f'{y}-{mes}':f'{y + 1}-{mes - 1}']

            df_const.loc["Skew", y] = o_station.skew(data=df_a)
            df_const.loc["CVQ", y] = o_station.cvq(data=df_a)
            df_const.loc["BFI", y] = o_station.bfi(data=df_a)
            df_const.loc["Q5", y] = o_station.q5(data=df_a)
            df_const.loc["Q95", y] = o_station.q95(data=df_a)

        s = df_const.shape[0]
        logs = math.log(s)

        z = 0

        for i in range(0, df_const.shape[0]):
            linha = df_const.values[i]
            linha = [x for x in linha if np.isnan(x) == False and np.isinf(x) == False]
            z += sum(linha)        

        hy = 0

        for i in df_const.index:
            yi = df_const.loc[i].to_list()
            yi = [x for x in yi if np.isnan(x) == False and np.isinf(x) == False]
            yi = sum(yi)
            hy += (yi / z) * math.log(yi / z)

        hy = -hy

        c = 1 - (hy / logs)

        return c

def result():
    df = pd.DataFrame(index=['Skew', 'qsp', 'cvq', 'bfi', 'q5', 'hfd', 'q95', 'lowfr', 'highfrvar', 'constancy'], columns = [c for c in lista_estacoes])

    for c in df.columns:
        o_station = Hydro_Sig(c)
        
        df.loc['Skew', c] = o_station.skew()
        df.loc['qsp', c] = o_station.qsp()[o_station.qsp().index[0]]
        df.loc['cvq', c] = o_station.cvq()
        df.loc['bfi', c] = o_station.bfi()
        df.loc['q5', c] = o_station.q5()
        df.loc['hfd', c] = o_station.hfd()
        df.loc['q95', c] = o_station.q95()
        df.loc['lowfr', c] = o_station.lowfr()
        df.loc['highfrvar', c] = o_station.highfrvar()
        df.loc['constancy', c] = o_station.constancy()

    return df

# Testes
# print(result())
