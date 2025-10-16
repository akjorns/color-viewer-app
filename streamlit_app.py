import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# --- App Title and Description ---
st.set_page_config(layout="wide")
# --- Custom CSS Styling ---
st.markdown("""
    <style>
    /* --- General Text Color --- */
    html, body, [class*="css"] {
        color: #EC460C !important;
    }

    /* --- Sidebar Text and Labels --- */
    section[data-testid="stSidebar"] * {
        color: #EC460C !important;
    }

    /* --- Dropdown (Multiselect) Styling --- */
    div[data-baseweb="select"] > div {
        color: #EC460C !important; /* text color inside dropdown */
        border-color: #EC460C !important; /* border */
    }

    div[data-baseweb="select"] svg {
        fill: #EC460C !important; /* arrow color */
    }

    /* --- Buttons (Select/Deselect All) --- */
    button[kind="secondary"], button[kind="primary"] {
        color: #EC460C !important;
        border: 1px solid #EC460C !important;
    }
    button[kind="secondary"]:hover, button[kind="primary"]:hover {
        background-color: #EC460C !important;
        color: white !important;
    }

    /* --- Title and Headers --- */
    h1, h2, h3, h4, h5, h6 {
        color: #EC460C !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Color Marking Analyzer")
st.write("""
This app visualizes your color data in the 3D CIE L*a*b* color space. Each point is colored according to its true RGB value.
Use the multi-select menu on the left to filter by group.
""")

# --- 1. Load Your Actual Data from CSV ---
@st.cache_data
def load_data():
    """Loads and validates data from the CSV file."""
    try:
        df = pd.read_csv("color_data.csv")
    except FileNotFoundError:
        st.error("Error: `color_data.csv` not found. Please make sure it's in your GitHub repository.")
        return None, None

    # Define the exact column names we expect
    required_coords = ['L_star', 'A_star', 'B_star']
    required_colors = ['R', 'G', 'B']
    required_info = ['ID (company, number)', 'Marking', 'Group']
    
    # Check if all required columns exist
    for col in required_coords + required_colors + required_info:
        if col not in df.columns:
            st.error(f"Critical Error: Column '{col}' is missing from your `color_data.csv` file. Please check the file and column headers.")
            return None, None
            
    # --- Data Cleaning and Validation ---
    for col in required_colors:
        s = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df[col] = np.clip(s, 0, 255).astype(int)

    # Get a sorted list of unique group names
    group_names = sorted(df['Group'].unique().astype(str))
    
    # Restructure the data
    grouped_data = []
    for name in group_names:
        group_df = df[df['Group'].astype(str) == name]
        grouped_data.append({
            "groupName": name,
            "data": group_df
        })
    return grouped_data, group_names

groups, group_names = load_data()

# --- 2. Sidebar for User Input ---
selected_groups = []
if groups:
    st.sidebar.header("Controls")

    # (EDIT: Add Select/Deselect All buttons)
    # Initialize session state to remember selections
    if 'selection' not in st.session_state:
        st.session_state['selection'] = group_names

    # Create columns for the buttons to appear side-by-side
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Select All", use_container_width=True):
        st.session_state['selection'] = group_names
    if col2.button("Deselect All", use_container_width=True):
        st.session_state['selection'] = []

    # The multiselect widget's state is now controlled by session_state
    selected_groups = st.sidebar.multiselect(
        'Select groups to display:',
        options=group_names,
        default=st.session_state['selection']
    )
    # Update the session state with the user's latest selection
    st.session_state['selection'] = selected_groups


# --- 3. Create the 3D Plot ---
fig = go.Figure()

# Add the L*a*b* axes lines
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 100], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[-128, 127], y=[0, 0], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-128, 127], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))

# Plot the data
if groups:
    for group in groups:
        group_name = group["groupName"]
        group_data = group["data"]
        
        is_visible = (group_name in selected_groups)
        
        # --- Create colors and hover text from the unique columns ---
        marker_colors = [f"rgb({row['R']}, {row['G']}, {row['B']})" for _, row in group_data.iterrows()]
        
        hover_texts = [
            f"<b>ID:</b> {row['ID (company, number)']}<br>" +
            f"<b>Marking:</b> {row['Marking']}<br>" +
            f"<b>Group:</b> {row['Group']}<br><br>" +
            f"<b>L*:</b> {row['L_star']:.2f}<br>" +
            f"<b>a*:</b> {row['A_star']:.2f}<br>" +
            f"<b>b*:</b> {row['B_star']:.2f}<extra></extra>"
            for _, row in group_data.iterrows()
        ]
        
        fig.add_trace(go.Scatter3d(
            # --- Use the renamed coordinate columns ---
            x=group_data['A_star'], 
            y=group_data['B_star'], 
            z=group_data['L_star'],
            mode='markers',
            marker=dict(
                size=7,
                opacity=1.0, # Make points fully opaque
                color=marker_colors # Apply true colors
            ),
            name=f"Group {group_name}",
            visible=is_visible,
            hovertemplate=hover_texts
        ))

# --- 4. Configure Layout ---
fig.update_layout(
    title_text="3D View of Color Data",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        annotations=[
            dict(x=0, y=0, z=105, text="<b>L*</b>", showarrow=False, font=dict(size=14)),
            dict(x=135, y=0, z=50, text="<b>a*</b>", showarrow=False, font=dict(size=14)),
            dict(x=0, y=135, z=50, text="<b>b*</b>", showarrow=False, font=dict(size=14))
        ],
        camera=dict(
            projection=dict(type='orthographic')
        )
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

