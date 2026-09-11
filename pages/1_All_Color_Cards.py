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

st.title("All Color Cards 3D Visualization")

# --- 1. Load Data ---
@st.cache_data
def load_master_data():
    try:
        # encoding='utf-8-sig' handles invisible BOM characters from Excel
        df = pd.read_csv("MasterColorData.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        st.error("Error: `MasterColorData.csv` not found. Please make sure it is in your GitHub repository root.")
        return None, None

    # Clean whitespace and BOM remnants from column headers
    df.columns = df.columns.astype(str).str.replace('\ufeff', '').str.strip()

    required_coords = ['L_star', 'A_star', 'B_star']
    required_colors = ['R', 'G', 'B']
    required_info = ['ID (company, number)', 'Card_Name']

    for col in required_coords + required_colors + required_info:
        if col not in df.columns:
            st.error(f"Critical Error: Column '{col}' is missing from `MasterColorData.csv`. Detected columns: {list(df.columns)}")
            return None, None

    # Clean numeric coordinates (replace comma decimals if present)
    for col in required_coords:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

    # Validate RGB values
    for col in required_colors:
        s = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = np.clip(s, 0, 255).astype(int)

    # Unique list of card names
    card_names = sorted(df['Card_Name'].dropna().unique().astype(str))

    card_data = []
    for name in card_names:
        sub_df = df[df['Card_Name'].astype(str) == name]
        card_data.append({"cardName": name, "data": sub_df})

    return card_data, card_names

# Explicitly assign variables from the loader
cards, card_names = load_master_data()

# --- 2. Sidebar Navigation & Selection ---
selected_cards = []
if cards and card_names:
    st.sidebar.header("Controls")

    if 'master_card_selection' not in st.session_state:
        st.session_state['master_card_selection'] = card_names

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Select All", use_container_width=True):
        st.session_state['master_card_selection'] = card_names
    if col2.button("Deselect All", use_container_width=True):
        st.session_state['master_card_selection'] = []

    selected_cards = st.sidebar.multiselect(
        'Select Color Cards to display:',
        options=card_names,
        default=st.session_state['master_card_selection']
    )
    st.session_state['master_card_selection'] = selected_cards

# --- 3. Build 3D Plot ---
fig = go.Figure()

# Axes lines (always visible, hidden from legend)
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[0, 0], z=[0, 100],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[-128, 127], y=[0, 0], z=[50, 50],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[-128, 127], z=[50, 50],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none',
    showlegend=False
))

# Plot each color card
if cards:
    for item in cards:
        card_name = item["cardName"]
        card_df = item["data"]

        is_visible = card_name in selected_cards

        marker_colors = [f"rgb({row['R']}, {row['G']}, {row['B']})" for _, row in card_df.iterrows()]

        hover_texts = [
            f"<span style='color:rgb({row['R']},{row['G']},{row['B']});'>"
            f"<b>ID:</b> {row['ID (company, number)']}<br>"
            f"<b>Card:</b> {row['Card_Name']}<br><br>"
            f"<b>L*:</b> {row['L_star']:.2f}<br>"
            f"<b>a*:</b> {row['A_star']:.2f}<br>"
            f"<b>b*:</b> {row['B_star']:.2f}</span><extra></extra>"
            for _, row in card_df.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=card_df['A_star'],
            y=card_df['B_star'],
            z=card_df['L_star'],
            mode='markers',
            marker=dict(size=7, opacity=1.0, color=marker_colors),
            name=card_name,
            visible=is_visible,
            hovertemplate="%{text}",
            text=hover_texts
        ))

# --- 4. Layout and Display ---
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-130, 130]),
        yaxis=dict(visible=False, range=[-130, 130]),
        zaxis=dict(visible=False, range=[-10, 110]),
        aspectmode='cube',  # Forces the 3D space to stay a perfect cube
        annotations=[
            dict(x=0, y=0, z=105, text="<b>L</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=135, y=0, z=50, text="<b>A</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=0, y=135, z=50, text="<b>B</b>", showarrow=False, font=dict(size=14, color="#F21578"))
        ],
        camera=dict(projection=dict(type='orthographic'))
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True,
    hoverlabel=dict(
        font_color="#F21578",
        bordercolor="#F21578",
        bgcolor="white"
    )
)

st.plotly_chart(fig, use_container_width=True)
