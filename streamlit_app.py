import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# --- App Title and Description ---
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

st.title("1910's Color Cards Color Data")

# --- 1. Load Your Actual Data from CSV ---
@st.cache_data
def load_data():
    """Loads and validates data from the CSV file."""
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
            
    for col in required_colors:
        s = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = np.clip(s, 0, 255).astype(int)

    # Sort group names numerically if possible
    def sort_key(val):
        try:
            return int(float(val))
        except ValueError:
            return val

    group_names = sorted(df['Group'].unique().astype(str), key=sort_key)
    
    grouped_data = []
    for name in group_names:
        group_df = df[df['Group'].astype(str) == name]
        grouped_data.append({
            "groupName": name,
            "data": group_df
        })
    return grouped_data, group_names

groups, group_names = load_data()

# --- 2. Create the 3D Plot ---
fig = go.Figure()

# Add the L*a*b* axes lines
fig.add_trace(go.Scatter3d(
    x=[0, 0],
