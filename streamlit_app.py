import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from streamlit_plotly_events import plotly_events

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
    .expanded-card {
        background-color: #fff;
        border-radius: 20px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
        padding: 30px;
        margin-top: 20px;
        text-align: center;
        transition: all 0.3s ease-in-out;
    }
    .color-box {
        width: 100%;
        height: 250px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.2);
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
        st.error("Error: `color_data.csv` not found.")
        return None, None

    required_coords = ['L_star', 'A_star', 'B_star']
    required_colors = ['R', 'G', 'B']
    required_info = ['ID (company, number)', 'Marking', 'Group']

    for col in required_coords + required_colors + required_info:
        if col not in df.columns:
            st.error(f"Missing column '{col}' in color_data.csv.")
            return None, None

    df['Group'] = df['Group'].fillna('n/a')

    for col in required_colors:
        s = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = np.clip(s, 0, 255).astype(int)

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

# Axes lines (always visible, not in legend)
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[0, 0], z=[0, 100],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none', showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[-128, 127], y=[0, 0], z=[50, 50],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none', showlegend=False
))
fig.add_trace(go.Scatter3d(
    x=[0, 0], y=[-128, 127], z=[50, 50],
    mode='lines', line=dict(color='black', width=4),
    hoverinfo='none', showlegend=False
))

# Plot each palette
if groups:
    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]

        is_numeric = group_name.replace('.', '', 1).isdigit()
        legend_label = f"palette {int(float(group_name))}" if is_numeric else f"palette {group_name}"

        marker_colors = [f"rgb({row['R']}, {row['G']}, {row['B']})" for _, row in group_data.iterrows()]

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
            text=hover_texts,
            customdata=group_data[['L_star', 'A_star', 'B_star', 'R', 'G', 'B',
                                   'ID (company, number)', 'Marking', 'Group']].values.tolist()
        ))

# --- 3. Layout ---
fig.update_layout(
    title_text="3D View of 1910's Colors",
    scene=dict(
        xaxis=dict(visible=False, range=[-128, 128]),
        yaxis=dict(visible=False, range=[-128, 128]),
        zaxis=dict(visible=False, range=[0, 100]),
        annotations=[
            dict(x=0, y=0, z=105, text="<b>L</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=135, y=0, z=50, text="<b>A</b>", showarrow=False, font=dict(size=14, color="#F21578")),
            dict(x=0, y=135, z=50, text="<b>B</b>", showarrow=False, font=dict(size=14, color="#F21578"))
        ],
        camera=dict(projection=dict(type='orthographic'))
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

# --- 4. Plotly chart with click detection ---
selected_points = plotly_events(fig, click_event=True, hover_event=False, override_height=700, key="color_plot")

# --- 5. Expanded card when a point is clicked ---
if selected_points:
    point = selected_points[0]
    # Find color info from customdata
    if "customdata" in point:
        data = point["customdata"]
        L, A, B, R, G, Bl, ID, Marking, Group = data
        st.markdown("<div class='expanded-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='color-box' style='background-color:rgb({R},{G},{Bl});'></div>", unsafe_allow_html=True)
        st.markdown(f"### 🎨 Palette {Group}")
        st.write(f"**ID (company, number):** {ID}")
        st.write(f"**Marking:** {Marking}")
        st.write(f"**L\*:** {L:.2f}  **a\*:** {A:.2f}  **b\*:** {B:.2f}")
        st.write(f"**RGB:** ({R}, {G}, {Bl})")
        st.markdown("</div>", unsafe_allow_html=True)
