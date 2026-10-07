import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.title("SimplyAnalytics Radius Data Viewer")

# Load dataset
data_path = "data/simplyanalytics_1_6_usa.csv"
df = pd.read_csv(data_path)

# Slider selection for radius (1 to 6 miles)
radius = st.slider("Select Radius (Miles)", min_value=1, max_value=6, value=1, step=1)

# Display selected radius
st.write(f"Selected Radius: **{radius} mile radius**")

# Interactive Map centered on Sarita's Restaurant
lat, lon = 29.691532913019, -95.219621361802
radius_meters = radius * 1609.34

m = folium.Map(location=[lat, lon], zoom_start=11)
folium.Marker([lat, lon], popup="Sarita's Restaurant", tooltip="Sarita's Restaurant").add_to(m)
folium.Circle(
    location=[lat, lon],
    radius=radius_meters,
    color="#3182bd",
    fill=True,
    fill_color="#3182bd",
    fill_opacity=0.2,
).add_to(m)

st_folium(m, width=700, height=450, returned_objects=[])

# Column selection based on radius
selected_column = f"{radius} mile radius"

# Select Attribute, chosen radius column, and USA
filtered_df = df[["Attribute", selected_column, "USA"]]

# Display simple table
st.dataframe(filtered_df, use_container_width=True)
