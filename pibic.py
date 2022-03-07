import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt

# Ler shape de minibacias e reservatórios
gdf_ach = gpd.read_file(r'C:\Users\pedro\OneDrive\Documentos\UFAL\PIBIC\Bacia Otto\ach_2017_5k.shp')
gdf_res = gpd.read_file(r'C:\Users\pedro\OneDrive\Documentos\UFAL\PIBIC\Reservatorios_do_Semiarido_Brasileiro\Reservatorios_do_Semiarido_Brasileiro.shp')

# Tratamento do geodataframe e intersecção do reservatório com as respcetivas minibacias
gdf_res.index = gdf_res['NM_RESERV']
reservatorio = gdf_res.loc['Sumé', 'geometry']
minibacia_res = gdf_ach[gdf_ach.intersects(reservatorio)]
bacia_res = gdf_ach[gdf_ach['cocursodag'].str.startswith(minibacia_res.cocursodag.values[0], na=False)]
bacia_res = bacia_res[bacia_res['cobacia'] >= minibacia_res.cobacia.values[0]]

# Estações pluviométricas/Fluviométricas afetadas
url = 'https://raw.githubusercontent.com/hydrobr/hydrobr/master/hydrobr/resources/ANAF_prec_stations.csv'  # Link atual: pluviométricas
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

estacoes_afetadas.to_file(r'C:\Users\pedro\OneDrive\Documentos\UFAL\PIBIC\Estações afetadas\estações_afetadas.shp')
