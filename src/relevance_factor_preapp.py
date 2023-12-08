import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import numpy as np
import json
from copy import deepcopy


# Add title and header
st.set_page_config(page_title="Migros next store's location in Zürich", # page title, displayed on the window/tab bar
                   page_icon="🟧", # favicon: icon that shows on the window/tab bar 
                   layout="centered", # use full width of the page
                   #menu_items={
                   #    'About': "WRITE WHAT YOUR PAGE IS ABOUT"
                   #}
)
#st.title("")
#st.header("Migros next store's location in Zürich")
st.markdown("# <span style='font-size:40px;'>Migros next store's location in Zürich</span>", unsafe_allow_html=True)
st.markdown("# <span style='font-size:30px;'>Best location according to KPIs</span>", unsafe_allow_html=True)

# Show procedure
st.write("To open a new store in a Kreis, a weighted linear model is proposed. The score of a Kreis is given by the")

centered_text = """ <div style="text-align: center;">
    Relevance Factor = a_1 w_1 + a_2 w_2 + a_3 w_3 + a_4 w_4
</div>
<br>
where a_i are KPIs of corresponding weigths w_i.
<br>
<br>
<div style="text-align: center;">
    <h5>The Kreis with the highest factor is the best location for installing a new store.</h5>
</div>
<hr>
"""
st.markdown(centered_text, unsafe_allow_html=True)


# First some Data Exploration
@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

# Get data for KPIs
Aldi_store_per_kreis=[2, 2, 0, 0, 1, 0, 1, 0, 2, 0, 3, 1]
Lidl_store_per_kreis=[1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 3, 1]
Coop_store_per_kreis=[6, 5, 6, 4, 5, 3, 3, 4, 9, 6, 8, 3]
Migros_store_per_kreis=[4, 4, 3, 3, 3, 2, 3, 2, 3, 2, 3, 1]

Total_store_num=[x_1 + x_2 + x_3 + x_4 for x_1, x_2, x_3, x_4 in zip(
    Aldi_store_per_kreis, Lidl_store_per_kreis, Coop_store_per_kreis, Migros_store_per_kreis)]


# KPI 1: a_1: number of migros stores/total number of stores in a kreis
a_1=[y_1/ y_2 for y_1, y_2 in zip(Migros_store_per_kreis,Total_store_num)]

# KPI 2: a_2: Current population density, normalized by the population density of Zurich
a_2=[0.675171,0.694047,1.212819,2.122174,1.655881,1.458411,0.542626,0.768098,1.005600,0.947106,1.205974,1.144783]

# KPI 3: a_3: Avergae income in a kreis (KCHF)
den_1 = pd.read_csv("./data/processed/average_income_per_kreis_sorted.csv")
mean_income=den_1['Median value of taxable income'].mean()
income_per_kreis=[76.38, 68.53, 58.32, 52.2, 71.07, 74.13, 89.27, 88.97, 57.0, 67.68, 55.3, 44.67]
a_3 = [i /mean_income for i in income_per_kreis]

# KPI 4: a_4: future population density 2040, normalized by the population density of Zurich
future_pop_density=[0.589022, 0.693816,1.206202,1.966494,1.746213,1.396008,0.527892,0.728034,1.000356,0.897879,1.262164,1.307432]
a_4 = [z_1 - z_2 for z_1, z_2 in zip(future_pop_density,a_2)]
a_4_percentage= [i *100 for i in a_4]

# 4 KPIs per district (12) will come from Vahid
#dummies = np.random.rand(12,4)
#KPIs = pd.DataFrame(dummies, columns=['a_1', 'a_2', 'a_3', 'a_4'])
#KPIs['Kreis'] = np.arange(1,13)
#KPIs = KPIs[['Kreis', 'a_1', 'a_2', 'a_3', 'a_4']]
KPIs = pd.DataFrame(list(zip(np.arange(1,13), a_1, a_2, a_3, a_4)), columns =['Kreis', 'a_1', 'a_2', 'a_3', 'a_4'])

#Weights
# Setting up columns
left_column, right_column = st.columns(2)

weights = np.zeros(4)
left_column.markdown("**a_1, MIGROS MARKET SHARE: Number of Migros stores in a Kreis / Total number of supermakets** (the lower, the better).")
weights[0] = -1.0 * left_column.number_input("Enter weight w_1:", min_value=0.0, max_value=10.0, value=1.0, step=0.5)

left_column.markdown("**a_2, CURRENT POPULATION DENSITY: Current population density in the Kreis / Population density of Zürich** (the higher, the better).")
weights[1] = left_column.number_input("Enter weight w_2:", min_value=0.0, max_value=10.0, value=1.0, step=0.5)

right_column.markdown("**a_3, INCOME LEVEL: Average income in the Kreis / Current average income in Zürich** (the higher, the better).")
weights[2] = right_column.number_input("Enter weight w_3:", min_value=0.0, max_value=10.0, value=1.0, step=0.5)

right_column.markdown("**a_4, FUTURE POPULATION DENSITY: Prediction (2040) of population density change / Population density of Zürich** (the higher, the better).")
weights[3] = right_column.number_input("Enter weight w_4:", min_value=0.0, max_value=10.0, value=1.0, step=0.5)


# Display the user input
st.markdown(f"Selected weights are w_1 = {weights[0]}, w_2 = {weights[1]}, w_3 = {weights[2]}, w_4 = {weights[3]}.")

# Compute the score per Kreis
relevance_factor = deepcopy(KPIs)
relevance_factor[['w_1a_1', 'w_2a_2', 'w_3a_3', 'w_4a_4']] = relevance_factor[['a_1', 'a_2', 'a_3', 'a_4']].mul(weights)
relevance_factor['score'] = relevance_factor[['w_1a_1', 'w_2a_2', 'w_3a_3', 'w_4a_4']].sum(axis=1)

kreis_recommendation = relevance_factor.rename(columns={'score': 'Relevance Factor', 'a_1':'Migros Market Share (a_1)', 'a_2':'Population Density (a_2)', 
                                                        'a_3':'Normalized AVG Income (a_3)', 'a_4':'Population Change by 2040 (a_4) (%)'})

# Plot the scores on map
with open("./data/raw/stzh.adm_stadtkreise_a.json") as response:
    kreise = json.load(response)

max_factor = kreis_recommendation['Relevance Factor'].max()
df2 = kreis_recommendation.loc[kreis_recommendation['Relevance Factor'] == max_factor]
recom_kreis = df2.values.tolist()[0][0]

st.markdown(f"**Based on the given weights, the recommendation is to consider opening a new Migros store in:**")
message = "Kreis " + str(int(recom_kreis))
markdown_text = f"""
<div style="background-color: lightgray; padding: 10px;">
    <h5>{message}</h5>
</div>
"""
st.markdown(markdown_text, unsafe_allow_html=True)

plotly_map = go.Figure(go.Choroplethmapbox( geojson=kreise, 
                                            locations=relevance_factor.Kreis,
                                            z=relevance_factor.score,
                                            featureidkey="properties.name",
                                            #
                                            #opacity=0.7,
                                            #width=700,
                                            #height=600,
                                            #range_color=[0.0, 35.0],
                                            #labels={"Kreis":"Kreis",
                                            #    "Score": "Score"},
                                            hovertemplate="<b>Kreis: %{location}</b><br>" +
                                            "Relevance Factor: %{z:.2f}<br>" +
                                            "<extra></extra>",
                                            #title=f"<b>Ranking according to weighted KPIs</b>",
                                            #color_scale="pubugn" #"viridis" #"pubugn",
                                            colorscale='Blues',
                                            colorbar=dict(title='Relevance Factor')
                                            #line=dict(
                                            #            color=kreise["properties"]['yellow'],
                                            #            width=2,  # Custom boundary width
                                            ))

plotly_map.update_layout(mapbox_center={"lat": 47.38, "lon": 8.54},
                         mapbox_style="carto-positron", 
                         mapbox_zoom=10.8,
                         margin={"r":0,"t":35,"l":0,"b":0},
                         font_family="Balto",
                         font_color="black",
                         hoverlabel={"bgcolor":"white", 
                                    "font_size":12,
                                    "font_family":"Balto"},
                        title={"font_size":20,
                                "xanchor":"center", "x":0.38,
                                "yanchor":"bottom", "y":0.96}
)

st.plotly_chart(plotly_map)

st.markdown("<hr>", unsafe_allow_html=True)

if st.checkbox("Show data"):
    #st.subheader("Original data:")
    st.dataframe(data=kreis_recommendation)