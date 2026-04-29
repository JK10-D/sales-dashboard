import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine():
    url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)

def get_kpis(region=None, categorie=None):
    filters, params = [], {}
    if region:
        filters.append("cl.region = :region")
        params['region'] = region
    if categorie:
        filters.append("p.categorie = :categorie")
        params['categorie'] = categorie
    where = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT
            SUM(c.montant)                                  AS ca_total,
            COUNT(c.id)                                     AS nb_commandes,
            AVG(c.montant)                                  AS panier_moyen,
            ROUND(AVG(CASE WHEN c.statut = 'Livré'
                  THEN 1.0 ELSE 0.0 END) * 100, 1)         AS taux_livraison
        FROM commandes c
        JOIN clients  cl ON c.client_id  = cl.id
        JOIN produits  p ON c.produit_id = p.id
        {where}
    """
    engine = get_engine()
    with engine.connect() as conn:
        result = pd.read_sql(text(query), conn, params=params)
    return result.iloc[0]

def get_ca_mensuel(region=None, categorie=None):
    filters, params = [], {}
    if region:
        filters.append("cl.region = :region")
        params['region'] = region
    if categorie:
        filters.append("p.categorie = :categorie")
        params['categorie'] = categorie
    where = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT
            DATE_TRUNC('month', c.date_cmd) AS mois,
            SUM(c.montant)                  AS ca_total
        FROM commandes c
        JOIN clients  cl ON c.client_id  = cl.id
        JOIN produits  p ON c.produit_id = p.id
        {where}
        GROUP BY DATE_TRUNC('month', c.date_cmd)
        ORDER BY mois
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    return df

def get_ca_par_categorie():
    query = """
        SELECT p.categorie,
               SUM(c.montant) AS ca_total
        FROM commandes c
        JOIN produits p ON c.produit_id = p.id
        WHERE c.statut = 'Livré'
        GROUP BY p.categorie
        ORDER BY ca_total DESC
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

def get_ca_par_region():
    query = """
        SELECT cl.region,
               SUM(c.montant)  AS ca_total,
               COUNT(c.id)     AS nb_commandes
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        GROUP BY cl.region
        ORDER BY ca_total DESC
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df

def get_top_clients(n=10):
    query = f"""
        SELECT cl.nom,
               cl.region,
               SUM(c.montant)  AS ca_total,
               COUNT(c.id)     AS nb_commandes
        FROM commandes c
        JOIN clients cl ON c.client_id = cl.id
        WHERE c.statut = 'Livré'
        GROUP BY cl.nom, cl.region
        ORDER BY ca_total DESC
        LIMIT {n}
    """
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    return df