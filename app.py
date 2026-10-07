import folium
import matplotlib.pyplot as plt
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

# 3. Aggregate totals across 1 to 6 miles and USA, reindex order
radius_cols = [f"{r} mile radius" for r in range(1, 7)]
age_grouped = age_df.groupby("Age Group")[radius_cols + ["USA"]].sum()
age_grouped = age_grouped.reindex(["15–24", "25–34", "35–54", "55+"])

# 4. Calculate percentage distributions across total population 15+
age_pct = (age_grouped / age_grouped.sum()) * 100

# 5. Plot 100% stacked bar chart with Under-35 trend line, highlighting selected slider radius
age_plot = age_pct.T.copy()
age_plot.index = ["1 mile"] + [f"{r} miles" for r in range(2, 7)] + ["U.S."]

fig_age, ax_age = plt.subplots(figsize=(10, 6))

# 100% stacked bars
age_plot.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 6),
    width=0.7,
    ax=ax_age
)

highlight_idx = radius - 1

# Add percentage labels inside each segment and highlight active slider radius
for container in ax_age.containers:
    for bar_idx, bar in enumerate(container):
        if bar_idx == highlight_idx:
            bar.set_edgecolor("#e74c3c")
            bar.set_linewidth(2.2)

        height = bar.get_height()

        # Only label segments large enough to read clearly
        if height >= 7:
            ax_age.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                f"{height:.1f}%",
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color="white"
            )

# Under-35 share = 15–24 + 25–34
under_35 = (
    age_plot["15–24"] +
    age_plot["25–34"]
)

x = range(len(age_plot))

# Trend line along the cumulative Under-35 boundary
ax_age.plot(
    x,
    under_35,
    marker="o",
    linewidth=2.5,
    color="black",
    label="Under 35"
)

# Label Under-35 trend and highlight active slider radius
for i, value in enumerate(under_35):
    is_active = (i == highlight_idx)
    text_color = "#e74c3c" if is_active else "black"
    ax_age.text(
        i,
        value + 2,
        f"Under 35: {value:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color=text_color
    )
    if is_active:
        ax_age.scatter(i, value, color="#e74c3c", s=100, zorder=5)

ax_age.set_title(
    "Sarita's Trade Area Skews Younger Than the U.S.",
    fontweight="bold",
    fontsize=14
)

ax_age.set_xlabel("")
ax_age.set_ylabel("Share of Population Age 15+ (%)")
ax_age.set_ylim(0, 105)

ax_age.grid(axis="y", linestyle="--", alpha=0.3)
ax_age.set_axisbelow(True)

ax_age.legend(
    title="Age Group",
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

# Highlight selected x-axis tick label
x_labels = ax_age.get_xticklabels()
plt.xticks(rotation=0)
if 0 <= highlight_idx < len(x_labels):
    x_labels[highlight_idx].set_color("#e74c3c")
    x_labels[highlight_idx].set_fontweight("bold")

plt.tight_layout()
st.pyplot(fig_age)

# --- Household Income Distribution Section ---
st.subheader("Household Income Distribution Compared with U.S. Average")

# 1. Filter dataset for B19001 attributes
income_df = df[df["Attribute"].str.contains(r"\[B19001\]", regex=True, na=False)].copy()

# 2. Map income groups matching notebook logic
def income_group(attribute):
    if any(x in attribute for x in [
        "Less than $10,000",
        "$10,000 to $14,999",
        "$15,000 to $19,999",
        "$20,000 to $24,999",
        "$25,000 to $29,999",
        "$30,000 to $34,999"
    ]):
        return "<$35k"
    elif any(x in attribute for x in [
        "$35,000 to $39,999",
        "$40,000 to $44,999",
        "$45,000 to $49,999",
        "$50,000 to $59,999",
        "$60,000 to $74,999"
    ]):
        return "$35k–$74,999"
    elif any(x in attribute for x in [
        "$75,000 to $99,999",
        "$100,000 to $124,999",
        "$125,000 to $149,999"
    ]):
        return "$75k–$149,999"
    else:
        return "$150k+"

income_df["Income Group"] = income_df["Attribute"].apply(income_group)

# 3. Aggregate totals across 1-6 miles and USA, reindex order
radius_cols = [f"{r} mile radius" for r in range(1, 7)]
income_grouped = income_df.groupby("Income Group")[radius_cols + ["USA"]].sum()
income_grouped = income_grouped.reindex(["<$35k", "$35k–$74,999", "$75k–$149,999", "$150k+"])

# 4. Calculate percentage point differences from USA across 1 to 6 miles
income_vs_usa = income_grouped[radius_cols].subtract(income_grouped["USA"], axis=0).T
income_vs_usa.index = ["1 mile"] + [f"{r} miles" for r in range(2, 7)]

# 5. Plot grouped bar chart highlighting the active slider radius
fig_inc, ax_inc = plt.subplots(figsize=(10, 6))
income_vs_usa.plot(kind="bar", width=0.75, ax=ax_inc)

highlight_idx = radius - 1

# Highlight bars for selected radius
for container in ax_inc.containers:
    for bar_idx, bar in enumerate(container):
        if bar_idx == highlight_idx:
            bar.set_edgecolor("#e74c3c")
            bar.set_linewidth(2.2)

    ax_inc.bar_label(
        container,
        fmt="%+.1f pp",
        padding=3,
        fontsize=8
    )

ax_inc.axhline(0, linewidth=1, color="black")
ax_inc.set_title("Household Income Distribution Compared with U.S. Average", fontweight="bold")
ax_inc.set_xlabel("")
ax_inc.set_ylabel("Difference from U.S. Average (percentage points)")
ax_inc.grid(axis="y", linestyle="--", alpha=0.4)
ax_inc.set_axisbelow(True)
ax_inc.legend(title="Household Income")

# Highlight selected x-axis tick label
x_labels = ax_inc.get_xticklabels()
if 0 <= highlight_idx < len(x_labels):
    x_labels[highlight_idx].set_color("#e74c3c")
    x_labels[highlight_idx].set_fontweight("bold")

plt.xticks(rotation=0)
plt.tight_layout()
st.pyplot(fig_inc)

# --- Hispanic & Spanish-Speaking Concentration Section ---
st.subheader("Demographic Concentration Above U.S. Average")

# 1. Filter Hispanic origin and Spanish language attributes from notebook logic
demo_rows = df[
    df["Attribute"].str.contains(
        r"Hispanic or Latino Origin|Language Spoken at Home \| Spanish",
        regex=True,
        na=False,
    )
].copy()

def get_metric_name(attr):
    if "Hispanic" in attr:
        return "Hispanic / Latino (%)"
    elif "Spanish" in attr:
        return "Spanish Spoken at Home (%)"
    return attr

demo_rows["Metric"] = demo_rows["Attribute"].apply(get_metric_name)

radius_cols = [f"{r} mile radius" for r in range(1, 7)]
cols_to_use = ["Metric"] + radius_cols + ["USA"]

demo_df = demo_rows[cols_to_use].set_index("Metric").T

# 2. Calculate percentage points above U.S. average across 1-6 miles
usa_vals = demo_df.loc["USA"].astype(float)
demo_vs_usa = demo_df.loc[radius_cols].astype(float).sub(usa_vals, axis=1)

demo_plot = demo_vs_usa.copy()
demo_plot.index = ["1 mile"] + [f"{r} miles" for r in range(2, 7)]

# 3. Create line plot highlighting the active slider radius
fig, ax = plt.subplots(figsize=(9, 5))
demo_plot.plot(kind="line", marker="o", linewidth=2.5, ax=ax)

# Highlight active radius with vertical guide line and larger red markers
highlight_idx = radius - 1
ax.axvline(
    x=highlight_idx,
    color="#e74c3c",
    linestyle="--",
    linewidth=1.8,
    alpha=0.75,
    label=f"Selected Radius ({radius} mile{'s' if radius > 1 else ''})",
)

for column in demo_plot.columns:
    for x_idx, y_val in enumerate(demo_plot[column]):
        if x_idx == highlight_idx:
            ax.scatter(x_idx, y_val, color="#e74c3c", s=110, zorder=5)
            ax.text(
                x_idx,
                y_val + 1.5,
                f"+{y_val:.1f} pp",
                ha="center",
                fontsize=9.5,
                fontweight="bold",
                color="#e74c3c",
            )
        else:
            ax.text(x_idx, y_val + 1.5, f"+{y_val:.1f} pp", ha="center", fontsize=9)

ax.axhline(0, linewidth=1, color="black")
ax.set_ylim(bottom=30, top=max(demo_plot.max()) + 8)

ax.set_title("Local Hispanic and Spanish-Speaking Concentration Above U.S. Average", fontweight="bold")
ax.set_xlabel("Distance from Sarita's")
ax.set_ylabel("Percentage Points Above U.S. Average")
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.set_axisbelow(True)
ax.legend(title="", loc="upper right")

plt.tight_layout()
st.pyplot(fig)
