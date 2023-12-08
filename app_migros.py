import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="Migros Team", 
                   page_icon="🟧", 
                   layout="wide", # use full width of the page
                   menu_items={
                       'About': "A Streamlit app to display the best location for next Migros store"
                   })

# Data
with open("stzh.adm_stadtkreise_a.json") as response:
    kreise = json.load(response)

with open("stzh.adm_verwaltungsquartiere_bes_p.json") as response:
    quarters = json.load(response)

df_stores =pd.read_csv("data/processed/all_stores_data.csv")
df_all_data =pd.read_csv("data/processed/all_data.csv")

st.title("Heading")

# Setting layout
# Setting up columns
left_column, middle_column, right_column = st.columns([3, 1, 1])

plot_types = ["Population Density", "Average Income Level"]
plot_type = left_column.radio("Choose Plot Type", plot_types)

# Widgets: selectbox
stores = ["All"]+sorted(pd.unique(df_stores['store']))
s = middle_column.selectbox("Choose a store", stores)

# Flow control and plotting
if s == "All":
    reduced_df = df_stores
else:
    reduced_df = df_stores[df_stores["store"] == s]

st.subheader("Population Density and Median Income Level per Kreis")
# Get unique store names and assign a color to each
unique_stores = df_stores['store'].unique()
store_colors = {
    'aldi': '#010160',
    'coop': '#DC3003',
    'lidl': '#FEEF02',
    'migros': '#FF6600'
}

# Create a scatter map for store locations
fig2 = go.Figure()

# Create a choropleth map for district density
fig2.add_trace(
    go.Choroplethmapbox(
        geojson=kreise,
        locations=df_stores['Kreis'],
        featureidkey="properties.name",
        z=df_stores['Kreis Density (population/km^2)'],
        colorscale='Blues',
        colorbar=dict(
            title='District Density',
            y=0.45,   
            len=0.8,
        ),
        hovertemplate="<b>%{location}</b><br>" +
                        "District Density: %{z:.2f}<br>" +
                        "<extra></extra>"
    )
)


# Iterate over unique store names and add traces
for store in unique_stores:
    store_data = reduced_df[reduced_df['store'] == store]

    # Add a scatter trace for each store
    if store == 'migros':
        # Customize markers for 'migros'
        fig2.add_trace(
            go.Scattermapbox(
                ids=store_data['store'],
                lat=store_data['latitude'],
                lon=store_data['longitude'],
                mode='markers',
                opacity=0.7,
                name=store.title(),
                text=store_data.apply(lambda x: f"{x['store'].title()}<br>{x['address']}<br>Kreis {x['Kreis']}", axis=1),
                marker=dict(
                    size=14,
                    color=store_colors[store],
                ),
                hovertemplate="<b>%{text}</b><br><extra></extra>"
            )
        )
    else:
        # Default scatter trace for other stores
        fig2.add_trace(
            go.Scattermapbox(
                ids=store_data['store'],
                lat=store_data['latitude'],
                lon=store_data['longitude'],
                mode='markers',
                name=store.title(),
                text=store_data.apply(lambda x: f"{x['store'].title()}<br>{x['address']}<br>Kreis {x['Kreis']}", axis=1),
                marker=dict(
                    size=10,
                    color=store_colors[store],
                ),
                hovertemplate="<b>%{text}</b><br><extra></extra>"
            )
        )
        
# Create a layout for the map
layout = go.Layout(
    mapbox=dict(
        center={"lat": 47.38, "lon": 8.54},
        style="carto-positron",
        zoom=11.4
    ),
    width=900,
    height=800,
    margin={"r": 0, "t": 35, "l": 0, "b": 0}
)

# Update the layout
fig2.update_layout(layout)

# Show the map
#st.plotly_chart(fig2)


#st.subheader("Median Income Level per Kreis")
# Get unique store names and assign a color to each
unique_stores = df_stores['store'].unique()
store_colors = {
    'aldi': '#010160',
    'coop': '#DC3003',
    'lidl': '#FEEF02',
    'migros': '#FF6600'
}

# Create a scatter map for store locations
fig3 = go.Figure()

# Create a choropleth map for district density
fig3.add_trace(
    go.Choroplethmapbox(
        geojson=kreise,
        locations=df_all_data['Kreis'],
        featureidkey="properties.name",
        z=df_all_data['Median value of taxable income'],
        colorscale='Blues',  # Choose a colorscale
        colorbar=dict(
            title='District Density',
            y=0.45,   
            len=0.8,
        ),
        hovertemplate="<b>%{location}</b><br>" +
                        "Median value of taxable income: %{z:.2f}<br>" +
                        "<extra></extra>"
    )
)


# Iterate over unique store names and add traces
for store in unique_stores:
    store_data = reduced_df[reduced_df['store'] == store]

    # Add a scatter trace for each store
    if store == 'migros':
        # Customize markers for 'migros'
        fig3.add_trace(
            go.Scattermapbox(
                ids=store_data['store'],
                lat=store_data['latitude'],
                lon=store_data['longitude'],
                mode='markers',
                opacity=0.7,
                name=store.title(),
                text=store_data.apply(lambda x: f"{x['store'].title()}<br>{x['address']}<br>Kreis {x['Kreis']}", axis=1),
                marker=dict(
                    size=14,
                    color=store_colors[store],
                ),
                hovertemplate="<b>%{text}</b><br><extra></extra>"
            )
        )
    else:
        # Default scatter trace for other stores
        fig3.add_trace(
            go.Scattermapbox(
                ids=store_data['store'],
                lat=store_data['latitude'],
                lon=store_data['longitude'],
                mode='markers',
                name=store.title(),
                text=store_data.apply(lambda x: f"{x['store'].title()}<br>{x['address']}<br>Kreis {x['Kreis']}", axis=1),
                marker=dict(
                    size=10,
                    color=store_colors[store],
                ),
                hovertemplate="<b>%{text}</b><br><extra></extra>"
            )
        )
        
# Create a layout for the map
layout = go.Layout(
    mapbox=dict(
        center={"lat": 47.38, "lon": 8.54},
        style="carto-positron",
        zoom=11.4
    ),
    width=900,
    height=800,
    margin={"r": 0, "t": 35, "l": 0, "b": 0}
)

# Update the layout
fig3.update_layout(layout)

# Show the map
#st.plotly_chart(fig3)


# Select which plot to show
if plot_type == "Population Density":
    st.plotly_chart(fig2)
else:
    st.plotly_chart(fig3)