import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

def affected_Stations(filename_otto, filename_res, type=1):
    """
    filename_otto: Caminho do arquivo shp contendo as minibacias;
    filename_res: Caminho do arquivo shp contendo os reservatórios;
    type: type = 1 localiza as estações pluviométricas e type = 2 as estações fluviométricas.
    """
    # Ler shape de minibacias e reservatórios
    gdf_ach = gpd.read_file(filename_otto)
    gdf_res = gpd.read_file(filename_res)

    # Tratamento do geodataframe e intersecção do reservatório com as respcetivas minibacias
    gdf_res.index = gdf_res['NM_RESERV']
    reservatorio = gdf_res.loc['Sumé', 'geometry']
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

# estacoes_afetadas.to_file(r'C:\Users\pedro\OneDrive\Documentos\UFAL\PIBIC\Estações afetadas\estações_afetadas.shp')
