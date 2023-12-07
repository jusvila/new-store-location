import pandas as pd
import json
import plotly.express as px
import streamlit as st


with open("stzh.adm_stadtkreise_a.json") as response:
    kreise = json.load(response)

with open("stzh.adm_verwaltungsquartiere_bes_p.json") as response:
    quarters = json.load(response)

st.title("Population per Kreis")

df = pd.read_csv("2030_pop_income.csv")

fig = px.choropleth_mapbox(
    df, 
    color="Population",
    geojson=kreise, 
    locations="Kreis", 
    featureidkey="properties.name",
    center={"lat": 47.38, "lon": 8.54},
    mapbox_style="carto-positron", 
    zoom=10.8,
    opacity=0.7,
    width=700,
    height=600,
    labels={
        "Kreis": "Kreis", 
        "Population": "Population", 
        "Median value of taxable income": "Median income"},
    hover_data = ["Median value of taxable income"],
    title="<b>Population per Kreis</b>",
    color_continuous_scale="Inferno",
)
fig.update_layout(
    margin={"r": 0, "t": 35, "l": 0, "b": 0},
    font_family="Balto",
    font_color="black",
    hoverlabel={"bgcolor": "white", "font_size": 12, "font_family": "Balto"},
    title={"font_size": 20, "xanchor": "center", "x": 0.38, "yanchor": "bottom", "y": 0.96},
    template = None
)


st.plotly_chart(fig)