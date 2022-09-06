from sklearn.metrics import davies_bouldin_score
from sklearn.cluster import KMeans
import hydrological_signatures
import pandas as pd

df_assinaturas = hydrological_signatures.result()

def padronizar_assinaturas(df_assinatura):
    """
    df_assinatura: Dataframe contendo as assinaturas hidrológicas por estação
    return: Novo DataFrame com as assinaturas padronizadas
    """
    df_assinatura = df_assinatura.dropna(axis=1)
    df_assinatura = df_assinatura.T

    for c in df_assinatura.columns:
        df_assinatura[c] = (df_assinatura[c]-df_assinatura[c].mean())/df_assinatura[c].std()
    
    return df_assinatura

df_assinaturas = padronizar_assinaturas(df_assinaturas)
df_assinaturas.dropna(axis=1, inplace=True)

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

