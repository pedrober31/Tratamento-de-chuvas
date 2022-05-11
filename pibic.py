from plotly.offline import iplot
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import hydrobr

def affected_Stations(filename_otto, filename_res, type = 1):
    """
    filename_otto: Path of the shp file containing the mini-basins;
    filename_res: Path of the shp file containing the reservoirs;
    type: type = 1 locates the rainfall stations and type = 2 the fluviometric stations.
    """
    # Ler shape de minibacias e reservatórios
    gdf_ach = gpd.read_file(filename_otto)
    gdf_res = gpd.read_file(filename_res)

    # Tratamento do geodataframe e intersecção do reservatório com as respectivas minibacias
    gdf_res.index = gdf_res['NM_RESERV']
    reservatorio = gdf_res.loc['Eng. Armando Ribeiro Gonçalves', 'geometry']
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
    estacoes_afetadas = gpd.sjoin(estacoes_ANA, bacia_res)

    return estacoes_afetadas

# Retornar as estações afetadas e gerar um sph do mesmo
# resultado = affected_Stations(r'Bacia Otto\ach_2017_5k.shp', 'Reservatorios_do_Semiarido_Brasileiro\Reservatorios_do_Semiarido_Brasileiro.shp', 2)
# resultado.to_file(r'C:\Users\pedro\Documents\UFAL\PIBIC\Estações_afetadas\estacoes_afetadas.shp')

class Flow(object):
    """
    class to obtain data from past stations in list form: station data and station flows.
    In addition to a visualization of data availability with gantt chart
    """
    def __init__(self, list_st=[]):
        self.list_st = list_st

    def track_back(self):
        """
        Track back stations datas
        """
        self.flow_st = hydrobr.get_data.ANA.list_flow_stations()
        self.flow_st.loc[self.flow_st['Code'].isin(self.list_st)]
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
