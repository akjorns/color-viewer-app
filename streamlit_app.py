import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- App Title and Description ---
st.set_page_config(layout="wide")
st.title("Interactive CIE Lab Color Analyzer")
st.write("""
This app visualizes color palettes in the 3D CIE L*a*b* color space.
Use the checkboxes on the left to compare palettes. You can rotate the 3D plot with your mouse.
""")

# --- 1. Data Generation (Cached for performance) ---
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

# --- 2. Sidebar for User Input (EDIT: Checkboxes) ---
st.sidebar.header("Controls")

# Initialize session state for each checkbox if it doesn't exist
for name in palette_names:
    if f'cb_{name}' not in st.session_state:
        st.session_state[f'cb_{name}'] = True  # Default to checked

# Add "Select All" and "Deselect All" buttons
col1, col2 = st.sidebar.columns(2)
if col1.button("Select All"):
    for name in palette_names:
        st.session_state[f'cb_{name}'] = True
if col2.button("Deselect All"):
    for name in palette_names:
        st.session_state[f'cb_{name}'] = False

st.sidebar.write("---") # Separator line

# Display a checkbox for each palette
selected_palettes = []
for name in palette_names:
    is_checked = st.sidebar.checkbox(name, key=f'cb_{name}')
    if is_checked:
        selected_palettes.append(name)


# --- 3. Create the 3D Plot ---
fig = go.Figure()

# Add the L*a*b* axes lines for context
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 100], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[-100, 100], y=[0, 0], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-100, 100], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))

# Add all palette color points to the figure
for palette in palettes:
    lab_points = palette["colors"]
    l, a, b = lab_points[:, 0], lab_points[:, 1], lab_points[:, 2]
    
    # Determine visibility based on checkbox selection
    is_visible = (palette["paletteName"] in selected_palettes)
    
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
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        annotations=[
            dict(x=0, y=0, z=105, text="<b>L*</b>", showarrow=False, font=dict(size=14)),
            dict(x=110, y=0, z=50, text="<b>a*</b>", showarrow=False, font=dict(size=14)),
            dict(x=0, y=110, z=50, text="<b>b*</b>", showarrow=False, font=dict(size=14))
        ],
        # (EDIT: Lock camera and projection to prevent zoom)
        # The 'orthographic' projection removes perspective, making zoom ineffective.
        # The 'eye' position sets a fixed, distant viewpoint.
        camera=dict(
            projection=dict(
                type='orthographic'
            ),
            eye=dict(x=2, y=2, z=2) # Lock the camera further away
        )
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

