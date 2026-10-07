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

# --- Age Demographic Section ---
st.subheader("Age Demographic Distribution (15+ Population)")

# 1. Filter dataset for B01001 attributes
age_df = df[df["Attribute"].str.contains(r"\[B01001\]", regex=True, na=False)].copy()

# 2. Map age groups matching project notebook logic
def age_group(attribute):
    if any(x in attribute for x in ["15 to 17", "18 and 19", "20 years", "21 years", "22 to 24"]):
        return "15–24"
    elif any(x in attribute for x in ["25 to 29", "30 to 34"]):
        return "25–34"
    elif any(x in attribute for x in ["35 to 39", "40 to 44", "45 to 49", "50 to 54"]):
        return "35–54"
    else:
        return "55+"

age_df["Age Group"] = age_df["Attribute"].apply(age_group)

# 3. Aggregate totals and reindex to preserve notebook ordering
age_grouped = age_df.groupby("Age Group")[[selected_column, "USA"]].sum()
age_grouped = age_grouped.reindex(["15–24", "25–34", "35–54", "55+"])

# 4. Calculate percentage distributions across total population 15+
age_pct = (age_grouped / age_grouped.sum()) * 100

# 5. Display comparison chart (Selected Radius vs USA)
st.bar_chart(age_pct)
