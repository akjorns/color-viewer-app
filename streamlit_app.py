import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# --- Page Setup ---
st.set_page_config(layout="wide")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        color: #F21578 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #F21578 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("1910's Color Cards Data")

# --- 1. Load Data ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("color_data.csv")
    except FileNotFoundError:
        st.error("Error: `color_data.csv` not found. Please make sure it's in your GitHub repository.")
        return None, None

    required_coords = ['L_star', 'A_star', 'B_star']
    required_colors = ['R', 'G', 'B']
    required_info = ['ID (company, number)', 'Marking', 'Group']

    for col in required_coords + required_colors + required_info:
        if col not in df.columns:
            st.error(f"Critical Error: Column '{col}' is missing from your `color_data.csv` file.")
            return None, None

    # Fill NaN groups with a readable name
    df['Group'] = df['Group'].fillna('n/a')

    # Clean color columns
    for col in required_colors:
        s = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = np.clip(s, 0, 255).astype(int)

    # --- Sort group names properly (numeric first, then text) ---
    def sort_key(x):
        s = str(x).strip()
        return (not s.replace('.', '', 1).isdigit(), float(s) if s.replace('.', '', 1).isdigit() else s)

    group_names = sorted(df['Group'].unique(), key=sort_key)

    grouped_data = []
    for name in group_names:
        group_df = df[df['Group'].astype(str).str.strip() == str(name).strip()]
        grouped_data.append({"groupName": name, "data": group_df})

    return grouped_data, group_names

groups, group_names = load_data()

# --- 2. Build 3D Plot ---
fig = go.Figure()

# Axes lines (always visible, hidden from legend)
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[0, 0], z=[-128, 127],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[-128, 127], y=[0, 0], z=[0, 0],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[-128, 127], z=[0, 0],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))

# Plot each palette
if groups:
    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]

        # Determine numeric vs text for legend
        is_numeric = group_name.replace('.', '', 1).isdigit()
        legend_label = f"palette {int(float(group_name))}" if is_numeric else f"palette {group_name}"

        # Marker colors
        marker_colors = [f"rgb({row['R']}, {row['G']}, {row['B']})" for _, row in group_data.iterrows()]

        # Hover texts
        hover_texts = [
            f"<b>ID:</b> {row['ID (company, number)']}<br>"
            f"<b>Marking:</b> {row['Marking']}<br>"
            f"<b>palette:</b> {legend_label.replace('palette ', '')}<br><br>"
            f"<b>L*:</b> {row['L_star']:.2f}<br>"
            f"<b>a*:</b> {row['A_star']:.2f}<br>"
            f"<b>b*:</b> {row['B_star']:.2f}<extra></extra>"
            for _, row in group_data.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=group_data['A_star'],
            y=group_data['B_star'],
            z=group_data['L_star'],
            mode='markers',
            marker=dict(size=7, opacity=1.0, color=marker_colors),
            name=legend_label,
            hovertemplate="%{text}",
            text=hover_texts
        ))

# --- 3. Layout and Display ---
fig.update_layout(
    title_text="3D View of 1910's Colors",
    scene=dict(
        xaxis=dict(visible=False, range=[-128, 127]),
        yaxis=dict(visible=False, range=[-128, 127]),
        zaxis=dict(visible=False, range=[-128, 127]),  # Extend L axis
        annotations=[
            dict(x=0, y=0, z=135, text="<b>L</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=135, y=0, z=0, text="<b>A</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=0, y=135, z=0, text="<b>B</b>", showarrow=False, font=dict(size=14, color="#F21578"))
        ],
        camera=dict(projection=dict(type='orthographic'))
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
