import pandas as pd
import streamlit as st

st.title("SimplyAnalytics Radius Data Viewer")

# Load dataset
data_path = "data/simplyanalytics_1_6_usa.csv"
df = pd.read_csv(data_path)

# Slider selection for radius (1 to 6 miles)
radius = st.slider("Select Radius (Miles)", min_value=1, max_value=6, value=1, step=1)

# Display selected radius
st.write(f"Selected Radius: **{radius} mile radius**")

# Column selection based on radius
selected_column = f"{radius} mile radius"

# Select Attribute, chosen radius column, and USA
filtered_df = df[["Attribute", selected_column, "USA"]]

# Display simple table
st.dataframe(filtered_df, use_container_width=True)
