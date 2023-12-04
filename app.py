import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import geopandas as gpd
import branca
import matplotlib.pyplot as plt
import branca.colormap as cm
from shapely import wkt

dfnor= pd.read_csv(r"./normalized_merged_data.csv")

gdf = gpd.read_file('ke_subcounty.shp')  

gdf['subcounty'] = gdf['subcounty'].str.upper()
columns_to_drop = ['country', 'province', 'provpcode', 'scpcode', 'county', 'dhis2_id','ctypcode']  
gdf = gdf.drop(columns=columns_to_drop)
merged_gdf = gdf.merge(dfnor, on='subcounty')
merged_gdf.to_csv("merged.csv",index=False)
df =pd.read_csv(r"./merged.csv")

st.set_page_config()
background_image = "https://drive.google.com/uc?export=view&id=1_Uz0hyhWFMyiaurp8kZ856E5Ygn3bZK6"
st.markdown(
    f"""
    <style>
        .stApp {{
            background-image: url({background_image});
            background-repeat: no-repeat;
            background-size: cover;
        }}

        .map-frame {{
            border: 25px solid #8B4513;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.4);
        }}
        
        .leaflet-container {{
            box-shadow: 0 0 20px 20px white;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("Seasonally NDVI Across Kenya by subcounty")
st.subheader("Created by Anja")
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')

selected_year = st.selectbox("Select Year:", gdf['year'].unique())
selected_month = st.selectbox("Select Month:", gdf['month'].unique())

filtered_gdf = gdf[(gdf['year'] == selected_year) & (gdf['month'] == selected_month)]

m = folium.Map(location=[0.821033, 37.716614], zoom_start=6)

min_ndvi, max_ndvi = filtered_gdf['NDVI'].min(), filtered_gdf['NDVI'].max()
colormap = cm.linear.YlGnBu_09.scale(min_ndvi, max_ndvi)

# Add NDVI data as polygons to the map
for _, row in filtered_gdf.iterrows():
    color = colormap(row['NDVI'])
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7
        },
        tooltip=f'Subcounty: {row["subcounty"]}<br>NDVI: {row["NDVI"]}'
    ).add_to(m)

# Add color scale to the map
colormap.caption = 'NDVI Scale'
colormap.add_to(m)

# Display the map
folium_static(m)