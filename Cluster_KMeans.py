import hydrological_signatures

def padronizar_assinaturas(df_assinatura):
    """
    df_assinatura: Dataframe contendo as assinaturas hidrológicas por estação
    return: Novo DataFrame com as assinaturas padronizadas
    """
    for c in df_assinatura.columns:
        if df_assinatura[c].std() != 0:
            df_assinatura[c] = (df_assinatura[c]-df_assinatura[c].mean())/df_assinatura[c].std()
        else:
            pass
    
    return df_assinatura

df_assinaturas = hydrological_signatures.result()
# print(padronizar_assinaturas(df_assinaturas))
