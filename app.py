import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# === CONFIGURATION GÉNÉRALE ===
st.set_page_config(page_title="📊 Dashboard Banque Mondiale", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>EXAMEN DE VISUALISATION DES DONNÉES</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Réalisé par : <strong>Jonathan KISSANGOU</strong></h4>", unsafe_allow_html=True)
st.markdown("---")

st.title("🌍 Tableau de bord interactif : Population, PIB, Téléphonie, Chômage")

# === CHARGEMENT DES DONNÉES ===
@st.cache_data
def charger_donnees():
    def nettoyer(df):
        df.dropna(subset=["Country Name", "Country Code"], inplace=True)
        df.columns = [col.split(" ")[0] if col[:4].isdigit() else col for col in df.columns]
        return df

    population = nettoyer(pd.read_excel("population.xlsx"))
    pib = nettoyer(pd.read_excel("pib.xlsx"))
    chomage = nettoyer(pd.read_excel("chomage.xlsx"))
    mobile = nettoyer(pd.read_excel("mobile.xlsx"))
    return population, pib, chomage, mobile

population, pib, chomage, mobile = charger_donnees()

annees = [str(a) for a in range(2010, 2023)]
annees_mobile = [str(a) for a in range(2010, 2016)]

# === FILTRAGE ===
AGREGATS = [
    # Mondial et groupes financiers
    "World", "IDA total", "IBRD only", "IDA & IBRD total", "IDA only", "IDA blend",
    "OECD members", "High income", "Low income", "Middle income", "Low & middle income",
    "Upper middle income", "Lower middle income",
    
    # Groupes économiques ou de développement
    "Early-demographic dividend", "Late-demographic dividend", "Post-demographic dividend", "Pre-demographic dividend",
    "Heavily indebted poor countries (HIPC)",
    "Least developed countries: UN classification",
    "Fragile and conflict affected situations",
    
    # Régions mondiales et sous-régions
    "East Asia & Pacific", "East Asia & Pacific (excluding high income)", "East Asia & Pacific (IDA & IBRD countries)",
    "South Asia", "South Asia (IDA & IBRD)",
    "Sub-Saharan Africa", "Sub-Saharan Africa (IDA & IBRD countries)", "Sub-Saharan Africa (excluding high income)",
    "Africa Eastern and Southern", "Africa Western and Central",
    "Latin America & Caribbean", "Latin America & the Caribbean (IDA & IBRD countries)",
    "Latin America & Caribbean (excluding high income)",
    "Middle East & North Africa", "Middle East & North Africa (excluding high income)", "Middle East & North Africa (IDA & IBRD countries)",
    "Europe & Central Asia", "Europe & Central Asia (IDA & IBRD countries)", "Europe & Central Asia (excluding high income)",
    "European Union", "Central Europe and the Baltics",
    "North America", "Arab World", "Euro area"
]  # (identique, liste non changée ici pour raccourcir)

def filtrer(df):
    return df[(df['Country Code'].str.len() == 3) & (~df['Country Name'].isin(AGREGATS))]

population = filtrer(population)
pib = filtrer(pib)
chomage = filtrer(chomage)
mobile = filtrer(mobile)

# === TRAITEMENT ===
population["Pop Moyenne"] = population[annees].mean(axis=1)
mobile["Mobile Moyenne"] = mobile[annees_mobile].mean(axis=1)
pib["PIB Total"] = pib[annees].mean(axis=1)
chomage[annees] = chomage[annees].fillna(0)
chomage["Chômage Moyen"] = chomage[annees].mean(axis=1)

# === PARTIE 1 : POPULATION & CARTE ===
st.markdown("## 📌 Partie 1 : Population et carte du monde")
st.success("1️⃣ **Top 5 des pays les plus peuplés**")
top5 = population[["Country Name", "Pop Moyenne"]].sort_values(by="Pop Moyenne", ascending=False).head(5)
st.dataframe(top5, use_container_width=True)

st.info("2️⃣ **Carte du monde basée sur la population moyenne (2010–2022)**")
fig1 = px.choropleth(population, locations="Country Code", color="Pop Moyenne", hover_name="Country Name", color_continuous_scale="Plasma")
st.plotly_chart(fig1, use_container_width=True)

# === PARTIE 2 : PIB ET CHÔMAGE ===
st.markdown("---")
st.markdown("## 📈 Partie 2 : PIB et Chômage")

st.warning("3️⃣ **Évolution du PIB (2010–2022)** pour la Chine, les États-Unis et l’Inde")
pays_selectionnes = ["China", "United States", "India"]
fig2, ax = plt.subplots(figsize=(10, 6))
for pays in pays_selectionnes:
    ligne = pib[pib["Country Name"] == pays]
    if not ligne.empty:
        ax.plot(annees, ligne[annees].values.flatten(), label=pays)
ax.set_title("Évolution du PIB (en USD)")
ax.set_xlabel("Année")
ax.set_ylabel("PIB")
ax.legend()
ax.grid(True)
st.pyplot(fig2)

st.success("4️⃣ **Pays avec le taux de chômage moyen le plus élevé**")
max_chom = chomage[["Country Name", "Chômage Moyen"]].sort_values(by="Chômage Moyen", ascending=False).head(1)
st.dataframe(max_chom)

st.info("5️⃣ **PIB vs Chômage pour le Congo, Rep.**")
pays = "Congo, Rep."
fig3, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(annees, pib[pib["Country Name"] == pays][annees].values.flatten(), color='blue')
ax1.set_ylabel("PIB", color='blue')
ax2 = ax1.twinx()
ax2.plot(annees, chomage[chomage["Country Name"] == pays][annees].values.flatten(), color='red', linestyle='--')
ax2.set_ylabel("Chômage", color='red')
plt.title(f"PIB et Chômage - {pays}")
plt.grid(True)
st.pyplot(fig3)

# === PARTIE 3 : Corrélation Téléphonie ===
df_merge = pib[["Country Name", "PIB Total"]].merge(
    population[["Country Name", "Pop Moyenne"]], on="Country Name").merge(
    mobile[["Country Name", "Mobile Moyenne"]], on="Country Name").merge(
    chomage[["Country Name", "Chômage Moyen"]], on="Country Name")
df_merge["PIB par Habitant"] = df_merge["PIB Total"] / df_merge["Pop Moyenne"]

st.markdown("---")
st.markdown("## 📡 Partie 3 : Téléphonie et développement")

st.warning("6️⃣ **Corrélation entre téléphonie et PIB/habitant**")
fig4, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df_merge, x="Mobile Moyenne", y="PIB par Habitant", hue="Chômage Moyen", palette="coolwarm", size="Chômage Moyen", ax=ax)
ax.set_title("Corrélation Téléphonie vs PIB/hab.")
ax.grid(True)
st.pyplot(fig4)

st.success("7️⃣ **Pays avec >100 téléphones/100 hab. et <5% chômage**")
st.dataframe(df_merge[(df_merge["Mobile Moyenne"] > 100) & (df_merge["Chômage Moyen"] < 5)])

cor_val = df_merge[['Mobile Moyenne', 'PIB par Habitant']].corr().iloc[0, 1]
st.info(f"8️⃣ **Corrélation mobile vs PIB/hab : {cor_val:.2f}**")

# === Données régionales uniquement ===
region_names = [
    "East Asia & Pacific", "South Asia", "Sub-Saharan Africa",
    "Africa Eastern and Southern", "Africa Western and Central",
    "Latin America & Caribbean", "Middle East & North Africa",
    "Europe & Central Asia", "North America", "Arab World"
]

# Rechargement des fichiers non filtrés
pop_all, pib_all, chom_all, mob_all = charger_donnees()

# === Ajout manuel des régions pour les pays présents dans mobile.xlsx ===
region_map_mobile = {
    "Argentina": "Latin America & Caribbean",
    "Australia": "East Asia & Pacific",
    "Brazil": "Latin America & Caribbean",
    "China": "East Asia & Pacific",
    "France": "Europe & Central Asia",
    "Germany": "Europe & Central Asia",
    "India": "South Asia",
    "Indonesia": "East Asia & Pacific",
    "Italy": "Europe & Central Asia",
    "Japan": "East Asia & Pacific",
    "Korea, Rep.": "East Asia & Pacific",
    "Mexico": "Latin America & Caribbean",
    "Netherlands": "Europe & Central Asia",
    "Russian Federation": "Europe & Central Asia",
    "Saudi Arabia": "Middle East & North Africa",
    "Spain": "Europe & Central Asia",
    "Switzerland": "Europe & Central Asia",
    "Turkiye": "Europe & Central Asia",
    "United Kingdom": "Europe & Central Asia",
    "United States": "North America",
    "Sudan": "Sub-Saharan Africa"
}

mobile["Region"] = mobile["Country Name"].map(region_map_mobile)

df_region_mobile = mobile.dropna(subset=["Region"]).copy()
df_region_mobile["Mobile Moyenne"] = df_region_mobile[annees_mobile].mean(axis=1)

# Calcul de la moyenne mobile par région
mobile_region = df_region_mobile.groupby("Region")["Mobile Moyenne"].mean().reset_index()

# Filtrer uniquement les régions de la liste
pop_region = pop_all[pop_all["Country Name"].isin(region_names)].copy()
pib_region = pib_all[pib_all["Country Name"].isin(region_names)].copy()
chom_region = chom_all[chom_all["Country Name"].isin(region_names)].copy()
mob_region = mobile["Region"]

# Calculs des moyennes
annees = [str(a) for a in range(2010, 2023)]
annees_mobile = [str(a) for a in range(2010, 2016)]

pop_region["Pop Moyenne"] = pop_region[annees].mean(axis=1)
pib_region["PIB Total"] = pib_region[annees].mean(axis=1)
chom_region[annees] = chom_region[annees].fillna(0)
chom_region["Chômage Moyen"] = chom_region[annees].mean(axis=1)

# Fusion finale
# df_region contient déjà PIB, Pop, Chômage avec colonne 'Region'
df_region = pib_region[["Country Name", "PIB Total"]].merge(
    pop_region[["Country Name", "Pop Moyenne"]], on="Country Name")
df_region = df_region.merge(chom_region[["Country Name", "Chômage Moyen"]], on="Country Name")
df_region.rename(columns={"Country Name": "Region"}, inplace=True)
df_region["PIB par Habitant"] = df_region["PIB Total"] / df_region["Pop Moyenne"]

# Ajouter la moyenne Mobile par région (si elle existe)
df_region = df_region.merge(mobile_region, on="Region", how="left")



# === PARTIE 4 : Analyse synthétique par région (Banque Mondiale) ===
st.markdown("---")
st.markdown("## 🔄 Partie 4 : Analyse synthétique par région (agrégats Banque Mondiale)")

# Liste officielle des régions à analyser
region_names = [
    "East Asia & Pacific", "South Asia", "Sub-Saharan Africa",
    "Africa Eastern and Southern", "Africa Western and Central",
    "Latin America & Caribbean", "Middle East & North Africa",
    "Europe & Central Asia", "North America", "Arab World"
]

# Filtrer les régions dans les fichiers originaux
pop_region = pop_all[pop_all["Country Name"].isin(region_names)].copy()
pib_region = pib_all[pib_all["Country Name"].isin(region_names)].copy()
chom_region = chom_all[chom_all["Country Name"].isin(region_names)].copy()

# Vérification que les régions sont bien présentes
regions_absentes = {
    "population.xlsx": set(region_names) - set(pop_region["Country Name"]),
    "pib.xlsx": set(region_names) - set(pib_region["Country Name"]),
    "chomage.xlsx": set(region_names) - set(chom_region["Country Name"])
}
for fichier, manquantes in regions_absentes.items():
    if manquantes:
        st.error(f"❌ Régions manquantes dans {fichier} : {manquantes}")
        st.stop()

# Calcul des indicateurs pour les régions (sauf mobile)
pop_region["Pop Moyenne"] = pop_region[annees].mean(axis=1)
pib_region["PIB Total"] = pib_region[annees].mean(axis=1)
chom_region[annees] = chom_region[annees].fillna(0)
chom_region["Chômage Moyen"] = chom_region[annees].mean(axis=1)

# Fusion des données
df_region = pib_region[["Country Name", "PIB Total"]].merge(
    pop_region[["Country Name", "Pop Moyenne"]], on="Country Name").merge(
    chom_region[["Country Name", "Chômage Moyen"]], on="Country Name")
df_region.rename(columns={"Country Name": "Region"}, inplace=True)
df_region["PIB par Habitant"] = df_region["PIB Total"] / df_region["Pop Moyenne"]

# Récupérer les moyennes mobile déjà calculées avec region_map_mobile
mobile_region = mobile.dropna(subset=["Region"]).groupby("Region")["Mobile Moyenne"].mean().reset_index()
df_region = df_region.merge(mobile_region, on="Region", how="left")  # fusion souple

st.markdown("### 1️⃣0️⃣ 🗺️ Carte du monde par PIB moyen (2010–2022)")

# Carte avec les données pays (déjà traitées au début)
fig_map_pib = px.choropleth(
    pib,
    locations="Country Code",
    color="PIB Total",
    hover_name="Country Name",
    color_continuous_scale="Viridis",
    title="Carte du monde - PIB moyen par pays"
)
fig_map_pib.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
st.plotly_chart(fig_map_pib, use_container_width=True)

# Sélection interactive
col1, col2 = st.columns(2)
region1 = col1.selectbox("🌍 Choisissez la région 1", df_region["Region"].unique())
region2 = col2.selectbox("🌍 Choisissez la région 2", df_region["Region"].unique(), index=1)

# Comparaison des indicateurs
st.markdown("### 1️⃣1️⃣ Comparaison des indicateurs moyens")
comparaison = df_region[df_region["Region"].isin([region1, region2])]
st.bar_chart(comparaison.set_index("Region")[["PIB Total", "Pop Moyenne", "Mobile Moyenne"]])

# === Évolution du chômage par région ===
st.markdown("### 1️⃣2️⃣ Évolution du chômage moyen par région")

fig5, ax = plt.subplots(figsize=(10, 6))

for reg in [region1, region2]:
    ligne = chom_region[chom_region["Country Name"] == reg]
    if not ligne.empty:
        ax.plot(annees, ligne[annees].values.flatten(), label=reg)

ax.set_title("Évolution du chômage moyen par région (2010–2022)")
ax.set_xlabel("Année")
ax.set_ylabel("Taux de chômage (%)")
ax.legend()
ax.grid(True)
st.pyplot(fig5)

# Corrélation
st.markdown("### 1️⃣3️⃣ Corrélation entre indicateurs")
corr = df_region[["PIB Total", "Pop Moyenne", "Mobile Moyenne", "Chômage Moyen"]].corr()
fig_corr, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap="YlGnBu", ax=ax)
ax.set_title("Corrélation entre indicateurs régionaux")
st.pyplot(fig_corr)
