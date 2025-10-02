import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- App Title and Description ---
st.set_page_config(layout="wide")
st.title("Interactive CIE Lab Color Palette Viewer")
st.write("""
This app visualizes color palettes in the 3D CIE L*a*b* color space.
Use the dropdown menu on the left to select a palette and see its colors plotted on the graph.
You can rotate, pan, and zoom the interactive 3D plot.
""")

# --- 1. Data Generation (Same as our Colab script) ---
# In a real app, you might load this from a CSV or JSON file.
@st.cache_data
def load_data():
    palettes = []
    np.random.seed(42)
    palette_names = [f"Palette {i+1}" for i in range(20)]
    for name in palette_names:
        center = np.random.rand(3) * np.array([60, 200, 200]) - np.array([0, 100, 100])
        colors_in_palette = center + (np.random.rand(10, 3) - 0.5) * 40
        palettes.append({
            "paletteName": name,
            "colors": colors_in_palette
        })
    return palettes, palette_names

palettes, palette_names = load_data()

# --- 2. Sidebar for User Input ---
st.sidebar.header("Controls")
selected_palette_name = st.sidebar.selectbox(
    'Select a Palette to Display:',
    ['Show All'] + palette_names
)

# --- 3. Create the 3D Plot ---
fig = go.Figure()

# Add the L*a*b* axes lines for context
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 100], mode='lines', name='L* Axis', line=dict(color='grey'), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[-100, 100], y=[0, 0], z=[50, 50], mode='lines', name='a* Axis', line=dict(color='grey'), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-100, 100], z=[50, 50], mode='lines', name='b* Axis', line=dict(color='grey'), hoverinfo='none'))

# Add all palette color points to the figure
for palette in palettes:
    lab_points = palette["colors"]
    l, a, b = lab_points[:, 0], lab_points[:, 1], lab_points[:, 2]
    
    # Determine visibility based on dropdown selection
    is_visible = (selected_palette_name == 'Show All' or selected_palette_name == palette["paletteName"])
    
    fig.add_trace(go.Scatter3d(
        x=a, y=b, z=l,
        mode='markers',
        marker=dict(size=6, opacity=0.8),
        name=palette["paletteName"],
        visible=is_visible,
        hovertemplate='<b>L*</b>: %{z:.2f}<br><b>a*</b>: %{x:.2f}<br><b>b*</b>: %{y:.2f}<extra></extra>'
    ))

# --- 4. Configure Layout and Display the Plot ---
fig.update_layout(
    title_text="3D View of Color Palettes",
    scene=dict(
        xaxis_title='a* (green → red)',
        yaxis_title='b* (blue → yellow)',
        zaxis_title='L* (black → white)'
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
