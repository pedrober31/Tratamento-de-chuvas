from shapely.geometry import Point
from plotly.offline import iplot
import matplotlib.pyplot as plt
import geopandas as gpd
import shapely.speedups
import pandas as pd
import hydrobr

# Realizar operações espaciais rapidamente
shapely.speedups.enable()

def not_affected_Stations(filename_otto, filename_res, name_res, type = 1):
    """
    filename_otto: Path of the shp file containing the mini-basins;
    filename_res: Path of the shp file containing the reservoirs;
    name_res: Name of the reservoir of reference
    type: type = 1 locates the rainfall stations and type = 2 the fluviometric stations.
    """
    # Ler shape de minibacias e reservatórios
    gdf_ach = gpd.read_file(filename_otto)
    gdf_res = gpd.read_file(filename_res)

    # Tratamento do geodataframe e intersecção do reservatório com as respectivas minibacias
    gdf_res.index = gdf_res['NM_RESERV']
    reservatorio = gdf_res.loc[name_res, 'geometry']
    minibacia_res = gdf_ach[gdf_ach.intersects(reservatorio)]
    bacia_res = gdf_ach[gdf_ach['cocursodag'].str.startswith(minibacia_res.cocursodag.values[0], na=False)]
    bacia_res = bacia_res[bacia_res['cobacia'] >= minibacia_res.cobacia.values[0]]

    # Estações pluviométricas/Fluviométricas afetadas
    if type == 1:
        url = 'https://raw.githubusercontent.com/hydrobr/hydrobr/master/hydrobr/resources/ANAF_prec_stations.csv'
    else:
        url = 'https://raw.githubusercontent.com/hydrobr/hydrobr/master/hydrobr/resources/ANAF_flow_stations.csv'
    
    estacoes_ANA = pd.read_csv(url)
    estacoes_ANA = estacoes_ANA.dropna(subset=['Latitude', 'Longitude'])
    estacoes_ANA['geometry'] = None

    for index, row in estacoes_ANA.iterrows():
        estacoes_ANA.loc[index, 'geometry'] = Point(row.Longitude, row.Latitude)

    estacoes_ANA = gpd.GeoDataFrame(estacoes_ANA, geometry='geometry')
    estacoes_ANA = estacoes_ANA.set_crs('epsg:4674')
    bacia_res = bacia_res.reset_index()
    bacia_res = bacia_res.drop(columns='index')
    estacoes_nafetadas = gpd.sjoin(estacoes_ANA, bacia_res)
    estacoes_nafetadas = estacoes_nafetadas[['Name', 'Code', 'Type', 'City', 'State', 'Latitude', 'Longitude', 'geometry']]

    return estacoes_nafetadas

class Flow():
    """
    class to obtain data from past stations in list form: station data and station flows.
    In addition to a visualization of data availability with gantt chart
    """
    def __init__(self, list_st=[]):
        self.list_st = list_st

    def track_back(self):
        """
        Track back stations
        """
        self.flow_st = hydrobr.get_data.ANA.list_flow_stations()
        self.flow_st = self.flow_st.loc[self.flow_st['Code'].isin(self.list_st)]
        return self.flow_st

    def data(self):
        """
        Obtain flow datas
        """
        self.flow_data = hydrobr.get_data.ANA.flow_data(self.list_st)
        return self.flow_data

    def gantt(self, width=1000, height=700, titlex='eixo x', titley='eixo y'):
        """
        Create html with gantt chart for visualization of data availability
        """
        gantt_chart = hydrobr.Plot.gantt(self.flow_data)
        gantt_chart.update_layout(
            autosize=False,
            width=width,
            height=height,
            xaxis_title = titlex,
            yaxis_title = titley,
            font=dict(family="Courier New, monospace", size=13)
        )
        iplot(gantt_chart)

def criar_geometria(estado=''):
    """
    estado: Estado que as estações desejadas serão filtradas
    return: Geodataframe contendo a coluna geometry para cada estação
    """
    estacoes = hydrobr.get_data.ANA.list_flow_stations(state=estado)
    estacoes = estacoes[['Name', 'Code', 'Type', 'City', 'State', 'Latitude', 'Longitude']]
    
    geometry = [Point(xy) for xy in zip(estacoes['Longitude'], estacoes['Latitude'])]
    
    gdf_estacoes = gpd.GeoDataFrame(estacoes, geometry=geometry)
    
    return gdf_estacoes

def estacoes_afetadas(caminho_otto, caminho_res, id, tipo_estacao, plotar=False):
    """
    caminho_otto: Caminho que contém o shp das ottobacias
    caminho_res: Caminho que contém o shp dos reservatórios de referência
    id: ID do reservatório de interesse
    tipo_estacao: Definir o tipo da estação, tipoo=1 (estação pluviométrica), tipo=2 (estação fluviométrica)
    plotar: Booleano para definir se o mapa contendo a bacia e as estações será plotado
    return: Dataframe contendo as estações não afetadas pelo reservatório de referência
    """
    reservatorios = gpd.read_file(caminho_res)
    bacias = gpd.read_file(caminho_otto)

    reservatorio_interesse = reservatorios[reservatorios['ID'] == id]
    ponto_interesse = reservatorio_interesse['geometry'].to_list()[0]

    bacia_interesse = bacias[bacias.contains(ponto_interesse)]
    codigo_interesse = bacia_interesse['nunivotto3'].to_list()[0]
    bacia_interesse = bacias[bacias['nunivotto3'] == codigo_interesse]

    estacoes_fluv = criar_geometria()
    estacoes_fluv.set_crs(epsg=4674, inplace=True)
    estacoes_interesse = gpd.sjoin(estacoes_fluv, bacia_interesse)
    estacoes_interesse = estacoes_interesse[['Name', 'Code', 'Type', 'City', 'State', 'Latitude', 'Longitude', 'geometry']]
    nome_reservatorio = reservatorios[reservatorios['ID'] == id]['NM_RESERV'].to_list()[0]
    estacoes_nafetadas = not_affected_Stations(caminho_otto, caminho_res, nome_reservatorio, tipo_estacao)
    estacoes_afetadas = estacoes_interesse.loc[list(set(estacoes_interesse.index).difference(set(estacoes_nafetadas.index)))]

    if plotar:
        fig, ax = plt.subplots()
        bacia_interesse.plot(ax=ax, facecolor='gray')
        estacoes_nafetadas.plot(ax=ax, facecolor='blue')
        estacoes_afetadas.plot(ax=ax, facecolor='green')
        reservatorio_interesse.plot(ax=ax, facecolor='red')
        plt.legend(['Estações Não Afetadas', 'Estações Afetadas', 'Reservatório'])
        plt.show()

    return estacoes_afetadas
