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

# Plot each palette
if groups:
    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]

        is_numeric = group_name.replace('.', '', 1).isdigit()
        legend_label = f"palette {int(float(group_name))}" if is_numeric else f"palette {group_name}"

        marker_colors = [f"rgb({row['R']}, {row['G']}, {row['B']})" for _, row in group_data.iterrows()]

        hover_texts = [
            f"<span style='color:rgb({row['R']},{row['G']},{row['B']});'>"
            f"<b>Marking:</b> {row['Marking']}<br>"
            f"<b>palette:</b> {legend_label.replace('palette ', '')}<br><br>"
            f"<b>L*:</b> {row['L_star']:.2f}<br>"
            f"<b>a*:</b> {row['A_star']:.2f}<br>"
            f"<b>b*:</b> {row['B_star']:.2f}</span><extra></extra>"
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
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
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

# --- 4. Isolated L-axis Graph ---
if groups:
    l_axis_fig = go.Figure()

    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]
        marker_colors = [f"rgb({row['R']},{row['G']},{row['B']})" for _, row in group_data.iterrows()]

        l_axis_fig.add_trace(go.Scatter(
            x=[group_name]*len(group_data),
            y=group_data['L_star'],
            mode='markers',
            marker=dict(size=10, color=marker_colors),
            name=f"palette {group_name}"
        ))

    l_axis_fig.update_layout(
        xaxis_title="Palette Group",
        yaxis_title="L* (Lightness)",
        plot_bgcolor="white",
        hoverlabel=dict(
            font_color="#F21578",
            bordercolor="#F21578",
            bgcolor="white"
        ),
        margin=dict(r=20, l=20, b=40, t=40)
    )

    st.plotly_chart(l_axis_fig, use_container_width=True)

# --- 4B. A* Axis Distribution ---
if groups:
    a_axis_fig = go.Figure()

    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]
        marker_colors = [f"rgb({row['R']},{row['G']},{row['B']})" for _, row in group_data.iterrows()]

        a_axis_fig.add_trace(go.Scatter(
            x=[group_name]*len(group_data),
            y=group_data['A_star'],
            mode='markers',
            marker=dict(size=10, color=marker_colors),
            name=f"palette {group_name}"
        ))

    a_axis_fig.update_layout(
        xaxis_title="Palette Group",
        yaxis_title="A* (Green–Red)",
        plot_bgcolor="white",
        hoverlabel=dict(
            font_color="#F21578",
            bordercolor="#F21578",
            bgcolor="white"
        ),
        margin=dict(r=20, l=20, b=40, t=40)
    )

    st.plotly_chart(a_axis_fig, use_container_width=True)

# --- 4C. B* Axis Distribution ---
if groups:
    b_axis_fig = go.Figure()

    for group in groups:
        group_name = str(group["groupName"]).strip()
        group_data = group["data"]
        marker_colors = [f"rgb({row['R']},{row['G']},{row['B']})" for _, row in group_data.iterrows()]

        b_axis_fig.add_trace(go.Scatter(
            x=[group_name]*len(group_data),
            y=group_data['B_star'],
            mode='markers',
            marker=dict(size=10, color=marker_colors),
            name=f"palette {group_name}"
        ))

    b_axis_fig.update_layout(
        xaxis_title="Palette Group",
        yaxis_title="B* (Blue–Yellow)",
        plot_bgcolor="white",
        hoverlabel=dict(
            font_color="#F21578",
            bordercolor="#F21578",
            bgcolor="white"
        ),
        margin=dict(r=20, l=20, b=40, t=40)
    )

    st.plotly_chart(b_axis_fig, use_container_width=True)



# --- 5. Marking-Ordered Graph ---
if groups:
    marking_fig = go.Figure()

    # Combine all groups into a single DataFrame for ordering
    all_data = pd.concat([group["data"] for group in groups], ignore_index=True)

    # Ensure 'Marking' is numeric for proper sorting
    all_data['Marking_numeric'] = pd.to_numeric(all_data['Marking'], errors='coerce')
    all_data = all_data.sort_values('Marking_numeric')

    marker_colors = [f"rgb({row['R']},{row['G']},{row['B']})" for _, row in all_data.iterrows()]

    hover_texts = [
        f"<b>Marking:</b> {row['Marking']}<br>"
        f"<b>Palette Group:</b> {row['Group']}<br>"
        f"<b>L*:</b> {row['L_star']:.2f}<br>"
        f"<b>a*:</b> {row['A_star']:.2f}<br>"
        f"<b>b*:</b> {row['B_star']:.2f}<extra></extra>"
        for _, row in all_data.iterrows()
    ]

    marking_fig.add_trace(go.Scatter(
        x=all_data['Marking_numeric'],
        y=[1]*len(all_data),  # just place all on the same horizontal line
        mode='markers',
        marker=dict(size=10, color=marker_colors),
        text=hover_texts,
        hoverinfo='text'
    ))

    marking_fig.update_layout(
        xaxis_title="Marking",
        yaxis=dict(visible=False),  # hide y-axis
        plot_bgcolor="white",
        hoverlabel=dict(
            font_color="#F21578",
            bordercolor="#F21578",
            bgcolor="white"
        ),
        margin=dict(r=20, l=20, b=40, t=40)
    )

    st.plotly_chart(marking_fig, use_container_width=True)



