from sklearn.metrics import davies_bouldin_score
from stations import criar_geometria
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import hydrological_signatures
import geopandas as gpd
import pandas as pd

# Obtenção da bacia e do trecho de rio de interesse
caminho_otto = r"C:\Users\pedro\OneDrive\Documentos\Pibic\Dados\ach_2017_5k\ach_2017_5k.shp"
caminho_res = r"C:\Users\pedro\OneDrive\Documentos\Pibic\Dados\Reservatorios_do_Semiarido_Brasileiro\Reservatorios_do_Semiarido_Brasileiro.shp"

reservatorios = gpd.read_file(caminho_res)
bacias = gpd.read_file(caminho_otto)

reservatorio_interesse = reservatorios[reservatorios['ID'] == 1421]
ponto_interesse = reservatorio_interesse['geometry'].to_list()[0]

bacia_interesse = bacias[bacias.contains(ponto_interesse)]
codigo_interesse = bacia_interesse['nunivotto3'].to_list()[0]
bacia_interesse = bacias[bacias['nunivotto3'] == codigo_interesse]

caminho_trecho = r"C:\Users\pedro\OneDrive\Documentos\Pibic\Dados\Trecho_Intersecção\Trecho_Intersecção.shp"
trecho_rio = gpd.read_file(caminho_trecho)
######################################################

df_assinaturas = hydrological_signatures.result()
df_assinaturas = df_assinaturas.T

def padronizar_assinaturas(df_assinatura):  # Criar outra padronização baseado no sistema de pontuação
    """
    df_assinatura: Dataframe contendo as assinaturas hidrológicas por estação
    return: Novo DataFrame com as assinaturas padronizadas
    """
    df_assinatura = df_assinatura.dropna(axis=1)
    df_assinatura = df_assinatura.T

    for c in df_assinatura.columns:
        df_assinatura[c] = (df_assinatura[c]-df_assinatura[c].mean())/df_assinatura[c].std()
    
    return df_assinatura

def clustering_kmeans(data):
    classes = []
    db = []

    for i in range(5):
        classes.append(i+2)
        kmeans = KMeans(n_clusters=i+2).fit(data)
        labels = kmeans.labels_
        db.append(davies_bouldin_score(data, labels))

    db_k = pd.DataFrame({'NClusters':classes,'DB - K means':db})
    db_k.set_index('NClusters', inplace=True)

    return db_k

def estacoes_cluster(n_clusters, df):
    kmeans = KMeans(n_clusters=n_clusters).fit(df)
    labels = kmeans.labels_

    df_estacoes_k = pd.DataFrame(data=labels, index=df_assinaturas.index, columns=['Labels'])

    estacoes = criar_geometria()
    estacoes = estacoes[estacoes['Code'].isin(df_estacoes_k.index)].reset_index(drop=True)
    geom = estacoes.geometry.to_list()

    gdf_estacoes_k = gpd.GeoDataFrame(data=df_estacoes_k, geometry=geom)

    return gdf_estacoes_k

gdf_estacoes_k = estacoes_cluster(2, df_assinaturas)

# Plotagem
fig, ax= plt.subplots(figsize=(15, 8))

bacia_interesse.plot(ax=ax, facecolor='gray')
trecho_rio.plot(ax=ax, zorder = 1, color='aqua', alpha=0.7, label='Rio')

gdf_estacoes_k[gdf_estacoes_k['Labels'] == 0].plot(ax=ax, label='Grupo 1', color='yellow', edgecolor='k', markersize=55)
gdf_estacoes_k[gdf_estacoes_k['Labels'] == 1].plot(ax=ax, label='Grupo 2', color='lime', edgecolor='k', markersize=55)
# gdf_estacoes_k[gdf_estacoes_k['Labels'] == 2].plot(ax=ax, label='Grupo 3', color='magenta', edgecolor='k', markersize=55)
# gdf_estacoes_k[gdf_estacoes_k['Labels'] == 3].plot(ax=ax, label='Grupo 4', color='blue', edgecolor='k', markersize=55)

reservatorio_interesse.plot(ax=ax, marker="D", color='red', label='Reservatório', edgecolor='k', markersize=60)

plt.legend(title='Agrupamentos', loc='upper left')
plt.xlim(-39, -36)
plt.ylim(-8, -5)

plt.show()
###########