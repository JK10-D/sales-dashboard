import streamlit as st
import plotly.express as px
from database import (get_kpis, get_ca_mensuel,
                      get_ca_par_categorie, get_ca_par_region, get_top_clients)

st.set_page_config(page_title="Dashboard Ventes", layout="wide")
st.title("Dashboard de suivi des ventes")
st.caption("Données en temps réel depuis PostgreSQL")

# ── Filtres sidebar ──
st.sidebar.header("Filtres")
region = st.sidebar.selectbox(
    "Région",
    ["Toutes", "Île-de-France", "PACA", "Auvergne-Rhône-Alpes", "Occitanie", "Bretagne"]
)
categorie = st.sidebar.selectbox(
    "Catégorie",
    ["Toutes", "Électronique", "Mobilier", "Vêtements", "Alimentation"]
)

r = None if region    == "Toutes" else region
c = None if categorie == "Toutes" else categorie

# ── KPIs ──
st.subheader("Indicateurs clés")
kpis = get_kpis(region=r, categorie=c)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires",  f"{kpis['ca_total']:,.0f} €")
col2.metric("Nb commandes",        f"{int(kpis['nb_commandes'])}")
col3.metric("Panier moyen",        f"{kpis['panier_moyen']:,.0f} €")
col4.metric("Taux de livraison",   f"{kpis['taux_livraison']} %")

st.divider()

# ── Graphiques ligne 1 ──
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("CA mensuel")
    df_mois = get_ca_mensuel(region=r, categorie=c)
    df_mois['mois'] = df_mois['mois'].astype(str).str[:7]
    fig1 = px.line(
        df_mois, x='mois', y='ca_total',
        labels={'mois': 'Mois', 'ca_total': 'CA (€)'}
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("CA par catégorie")
    df_cat = get_ca_par_categorie()
    fig2 = px.bar(
        df_cat, x='categorie', y='ca_total',
        labels={'categorie': 'Catégorie', 'ca_total': 'CA (€)'},
        color='categorie'
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Graphiques ligne 2 ──
col_c, col_d = st.columns(2)

with col_c:
    st.subheader("CA par région")
    df_region = get_ca_par_region()
    fig3 = px.bar(
        df_region, x='region', y='ca_total',
        labels={'region': 'Région', 'ca_total': 'CA (€)'},
        color='region'
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("Répartition des commandes par région")
    fig4 = px.pie(
        df_region, names='region', values='nb_commandes'
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Top clients ──
st.subheader("Top 10 clients")
st.dataframe(
    get_top_clients(10).rename(columns={
        'nom':          'Client',
        'region':       'Région',
        'ca_total':     'CA total (€)',
        'nb_commandes': 'Nb commandes'
    }),
    use_container_width=True
)