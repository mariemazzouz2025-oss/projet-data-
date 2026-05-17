# Importation des librairies nécessaires
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Chargement et nettoyage du dataset

# Charger le fichier Excel (Online Retail Dataset)
df = pd.read_excel("Online Retail.xlsx", engine="openpyxl")

# Supprimer les lignes avec CustomerID manquant (clients inconnus)
df = df.dropna(subset=["CustomerID"])

# Retirer les transactions annulées (InvoiceNo commence par 'C')
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]

# Supprimer les quantités négatives ou nulles
df = df[df["Quantity"] > 0]

# Supprimer les prix négatifs ou nuls
df = df[df["UnitPrice"] > 0]

# Créer une colonne TotalPrice = Quantity × UnitPrice
df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

# Convertir InvoiceDate en format datetime
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# Ajouter colonnes dérivées pour l’analyse temporelle
df["Year"] = df["InvoiceDate"].dt.year
df["Month"] = df["InvoiceDate"].dt.month
df["Day"] = df["InvoiceDate"].dt.day

# Sidebar interactive (Filtres)
st.sidebar.header("Filtres")

# Filtre par pays
pays = st.sidebar.selectbox("Choisir un pays", df["Country"].unique())

# Filtre par année
annee = st.sidebar.selectbox("Choisir une année", df["Year"].unique())

# Appliquer les filtres sélectionnés
df_filtre = df[(df["Country"] == pays) & (df["Year"] == annee)]

# Titre principal du dashboard
st.title("Dashboard E-commerce - Online Retail Dataset")

# Organisation en onglets
tab1, tab2, tab3 = st.tabs(["Ventes", "Produits", "Clients"])

# Onglet Ventes
with tab1:
    st.subheader("Analyse des ventes")

    # Calcul des KPI principaux
    ca_total = df_filtre["TotalPrice"].sum()
    nb_commandes = df_filtre["InvoiceNo"].nunique()
    nb_clients = df_filtre["CustomerID"].nunique()
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0

    # Affichage des KPI sous forme de métriques
    st.metric("Chiffre d’affaires total", f"{ca_total:,.2f} £")
    st.metric("Nombre de commandes", nb_commandes)
    st.metric("Nombre de clients uniques", nb_clients)
    st.metric("Panier moyen", f"{panier_moyen:,.2f} £")

    # Visualisation : évolution mensuelle du CA
    st.subheader("Évolution mensuelle du chiffre d’affaires")
    ca_mensuel = df_filtre.groupby("Month")["TotalPrice"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=ca_mensuel, x="Month", y="TotalPrice", marker="o", ax=ax)
    ax.set_ylabel("CA (£)")
    st.pyplot(fig)

# Onglet Produits 
with tab2:
    st.subheader("Analyse des produits")

    # Top 10 produits par chiffre d’affaires
    top_ca_produits = df_filtre.groupby("Description")["TotalPrice"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    top_ca_produits.plot(kind="bar", ax=ax)
    ax.set_ylabel("CA (£)")
    st.subheader("Top 10 produits par chiffre d’affaires")
    st.pyplot(fig)

    # Top 10 pays par chiffre d’affaires (global, pas filtré)
    ventes_par_pays = df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,4))
    ventes_par_pays.plot(kind="bar", ax=ax, color="orange")
    ax.set_ylabel("CA (£)")
    st.subheader("Top 10 pays par chiffre d’affaires (global)")
    st.pyplot(fig)

# Onglet Clients
with tab3:
    st.subheader("Analyse des clients")

    # Identifier la première commande de chaque client
    premiere_commande = df_filtre.groupby("CustomerID")["InvoiceDate"].min().reset_index()
    premiere_commande.columns = ["CustomerID", "PremiereDate"]

    # Fusionner avec dataset filtré
    df_clients = df_filtre.merge(premiere_commande, on="CustomerID")

    # Ajouter colonne "TypeClient" (Nouveau vs Récurrent)
    df_clients["TypeClient"] = df_clients.apply(
        lambda x: "Nouveau" if x["InvoiceDate"] == x["PremiereDate"] else "Récurrent",
        axis=1
    )

    # Calcul du CA par type de client
    segmentation = df_clients.groupby("TypeClient")["TotalPrice"].sum()

    # Visualisation segmentation clients
    fig, ax = plt.subplots()
    segmentation.plot(kind="bar", ax=ax, color=["green","blue"])
    ax.set_ylabel("CA (£)")
    st.subheader("Segmentation clients : Nouveaux vs Récurrents")
    st.pyplot(fig)

   

