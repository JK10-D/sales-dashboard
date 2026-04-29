from faker import Faker
import psycopg2
import random
from dotenv import load_dotenv
import os

load_dotenv()
fake = Faker('fr_FR')

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

def insert_clients(conn, n=200):
    regions = ['Île-de-France', 'PACA', 'Auvergne-Rhône-Alpes', 'Occitanie', 'Bretagne']
    with conn.cursor() as cur:
        for _ in range(n):
            cur.execute("""
                INSERT INTO clients (nom, email, region)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, (fake.name(), fake.email(), random.choice(regions)))
    conn.commit()
    print(f"{n} clients insérés")

def insert_produits(conn):
    produits = [
        ('Laptop Pro',         'Électronique',  1299.99),
        ('Smartphone X',       'Électronique',   799.99),
        ('Chaise Ergonomique', 'Mobilier',        349.99),
        ('Bureau Standing',    'Mobilier',        599.99),
        ('T-Shirt Premium',    'Vêtements',        39.99),
        ('Veste Hiver',        'Vêtements',       129.99),
        ('Café Bio 500g',      'Alimentation',     12.99),
        ('Huile d Olive',      'Alimentation',      8.99),
    ]
    with conn.cursor() as cur:
        for nom, cat, prix in produits:
            cur.execute("""
                INSERT INTO produits (nom, categorie, prix_unitaire)
                VALUES (%s, %s, %s)
            """, (nom, cat, prix))
    conn.commit()
    print(f"{len(produits)} produits insérés")

def insert_commandes(conn, n=1000):
    statuts = ['Livré', 'Livré', 'Livré', 'En cours', 'Annulé']
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM clients")
        client_ids = [r[0] for r in cur.fetchall()]

        cur.execute("SELECT id, prix_unitaire FROM produits")
        produits = cur.fetchall()

        for _ in range(n):
            produit = random.choice(produits)
            qte     = random.randint(1, 10)
            cur.execute("""
                INSERT INTO commandes
                    (client_id, produit_id, quantite, montant, statut, date_cmd)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                random.choice(client_ids),
                produit[0],
                qte,
                round(float(produit[1]) * qte, 2),
                random.choice(statuts),
                fake.date_between(start_date='-1y', end_date='today')
            ))
    conn.commit()
    print(f"{n} commandes insérées")

if __name__ == '__main__':
    print("Démarrage du pipeline d'ingestion...")
    conn = get_connection()
    insert_clients(conn)
    insert_produits(conn)
    insert_commandes(conn)
    conn.close()
    print("Pipeline terminé avec succès !")