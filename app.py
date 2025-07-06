import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# === Configuration de la page ===
st.set_page_config(page_title="Dashboard Banque Mondiale", layout="wide")
st.markdown("<h1 style='text-align: center; color: navy;'>EXAMEN DE VISUALISATION DES DONNÉES</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: gray;'>Jonathan KISSANGOU</h3>", unsafe_allow_html=True)

st.markdown("---")
st.title("🌍 Tableau de bord interactif : Population, PIB, Téléphonie, Chômage")


# === Chargement des fichiers ===
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

# === Filtrage des agrégats ===
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
]

def filtrer(df):
    return df[(df['Country Code'].str.len() == 3) & (~df['Country Name'].isin(AGREGATS))]

population = filtrer(population)
pib = filtrer(pib)
chomage = filtrer(chomage)
mobile = filtrer(mobile)

# === Moyennes ===
population["Pop Moyenne"] = population[annees].mean(axis=1)
mobile["Mobile Moyenne"] = mobile[annees_mobile].mean(axis=1)
pib["PIB Total"] = pib[annees].mean(axis=1)
chomage[annees] = chomage[annees].fillna(0)
chomage["Chômage Moyen"] = chomage[annees].mean(axis=1)

# === Top 5 ===
st.subheader("Partie 1")
st.subheader("1. Top 5 des pays les plus peuplés")
top5 = population[["Country Name", "Pop Moyenne"]].sort_values(by="Pop Moyenne", ascending=False).head(5)
st.dataframe(top5)

# === Carte population ===
st.subheader("2. 📌 Carte du monde - Population moyenne")
fig1 = px.choropleth(population, locations="Country Code", color="Pop Moyenne", hover_name="Country Name", color_continuous_scale="Plasma")
st.plotly_chart(fig1, use_container_width=True)

# === Évolution PIB ===
st.markdown("---")
st.subheader("Partie 2")
st.subheader("3. 📈 Évolution du PIB pour quelques pays")
pays_selectionnes = ["China", "United States", "India"]
fig2, ax = plt.subplots(figsize=(10, 6))
for pays in pays_selectionnes:
    ligne = pib[pib["Country Name"] == pays]
    if not ligne.empty:
        ax.plot(annees, ligne[annees].values.flatten(), label=pays)
ax.set_title("Évolution du PIB (2010–2022)")
ax.set_xlabel("Année")
ax.set_ylabel("PIB (USD)")
ax.legend()
ax.grid(True)
st.pyplot(fig2)

# === Chômage max ===
st.subheader("4. 📉 Taux de chômage le plus élevé")
max_chom = chomage[["Country Name", "Chômage Moyen"]].sort_values(by="Chômage Moyen", ascending=False).head(1)
st.dataframe(max_chom)

# === Graphique combiné ===
st.subheader("5. 📊 PIB vs Chômage pour Congo, Rep.")
pays = "Congo, Rep."
pib_vals = pib[pib["Country Name"] == pays][annees].values.flatten()
chom_vals = chomage[chomage["Country Name"] == pays][annees].values.flatten()
fig3, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(annees, pib_vals, color='blue')
ax1.set_ylabel("PIB", color='blue')
ax2 = ax1.twinx()
ax2.plot(annees, chom_vals, color='red', linestyle='--')
ax2.set_ylabel("Chômage", color='red')
plt.title(f"PIB et Chômage - {pays}")
plt.grid(True)
st.pyplot(fig3)

# === Corrélation ===
df_merge = pib[["Country Name", "PIB Total"]].merge(
    population[["Country Name", "Pop Moyenne"]], on="Country Name")
df_merge = df_merge.merge(mobile[["Country Name", "Mobile Moyenne"]], on="Country Name")
df_merge = df_merge.merge(chomage[["Country Name", "Chômage Moyen"]], on="Country Name")
df_merge["PIB par Habitant"] = df_merge["PIB Total"] / df_merge["Pop Moyenne"]

st.subheader("Partie 3")
st.subheader("6. 📡 Corrélation Téléphonie - PIB/Hab")
fig4, ax = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=df_merge, x="Mobile Moyenne", y="PIB par Habitant", hue="Chômage Moyen", palette="coolwarm", size="Chômage Moyen", ax=ax)
ax.set_title("Corrélation entre la téléphonie et le PIB/hab")
ax.grid(True)
st.pyplot(fig4)

st.write(f"**7. 📌 Pays avec forte pénétration téléphonique et faible chômage :**")
st.dataframe(df_merge[(df_merge["Mobile Moyenne"] > 100) & (df_merge["Chômage Moyen"] < 5)])
st.write(f"8. 📈 Corrélation : **{df_merge[['Mobile Moyenne', 'PIB par Habitant']].corr().iloc[0,1]:.2f}**")

# === Partie 4 : Analyse synthétique ===
st.markdown("---")
st.subheader("Partie 4")
st.subheader("9. 🔄 Analyse synthétique par région")
region_map = {
    "Congo, Rep.": "Afrique centrale", "France": "Europe", "United States": "Amérique du Nord",
    "China": "Asie", "India": "Asie", "Germany": "Europe", "Nigeria": "Afrique de l'Ouest",
    "Brazil": "Amérique latine", "South Africa": "Afrique australe", "Canada": "Amérique du Nord"
}

df_region = df_merge.copy()
df_region["Region"] = df_region["Country Name"].map(region_map)
df_region.dropna(subset=["Region"], inplace=True)

col1, col2 = st.columns(2)
region1 = col1.selectbox("Région 1", df_region["Region"].unique())
region2 = col2.selectbox("Région 2", df_region["Region"].unique(), index=1)

st.markdown("### 10. 🌐 Comparaison des indicateurs")
comparaison = df_region[df_region["Region"].isin([region1, region2])]
st.bar_chart(comparaison.groupby("Region")[["PIB Total", "Pop Moyenne", "Mobile Moyenne"]].mean())

st.markdown("### 11. 📊 Evolution du chômage")
fig5, ax = plt.subplots(figsize=(10, 6))
for reg in [region1, region2]:
    pays_reg = [k for k, v in region_map.items() if v == reg]
    sous_df = chomage[chomage["Country Name"].isin(pays_reg)]
    if not sous_df.empty:
        ax.plot(annees, sous_df[annees].mean(), label=reg)
ax.set_title("11. Évolution du chômage")
ax.legend()
ax.grid(True)
st.pyplot(fig5)

st.markdown("### 12. 🌟 Corrélation entre indicateurs")
corr = df_region[["PIB Total", "Pop Moyenne", "Mobile Moyenne", "Chômage Moyen"]].corr()
fig6, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap="YlGnBu", ax=ax)
ax.set_title("Corrélation entre indicateurs")
st.pyplot(fig6)
