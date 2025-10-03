import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd # Import the pandas library

# --- App Title and Description ---
st.set_page_config(layout="wide")
st.title("Color Marking Analyzer")
st.write("""
This app visualizes your color data in the 3D CIE L*a*b* color space.
Use the multi-select menu on the left to filter by group.
""")

# --- 1. Load Your Actual Data from CSV ---
# This function reads the CSV and processes it.
@st.cache_data
def load_data():
    """Loads color data from the CSV file and groups it."""
    try:
        # Read the csv file from your GitHub repository
        df = pd.read_csv("color_data.csv")
    except FileNotFoundError:
        st.error("Error: `color_data.csv` not found. Please make sure it's in your GitHub repository.")
        return [], []

    # Get a sorted list of unique group names
    # We convert to string to handle any group numbers correctly.
    group_names = sorted(df['Group'].unique().astype(str))
    
    # Restructure the data into a list of dictionaries, similar to our old format
    grouped_data = []
    for name in group_names:
        # Filter the dataframe for the current group
        group_df = df[df['Group'].astype(str) == name]
        
        # Store the relevant data for this group
        grouped_data.append({
            "groupName": name,
            "data": group_df
        })
        
    return grouped_data, group_names

# Load the data
groups, group_names = load_data()

# --- 2. Sidebar for User Input (Multi-select) ---
if groups: # Only show controls if data was loaded successfully
    st.sidebar.header("Controls")
    selected_groups = st.sidebar.multiselect(
        'Select groups to display:',
        options=group_names,
        default=group_names  # Default to showing all groups
    )

# --- 3. Create the 3D Plot ---
fig = go.Figure()

# Add the L*a*b* axes lines for context
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 100], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[-100, 100], y=[0, 0], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-100, 100], z=[50, 50], mode='lines', line=dict(color='black', width=4), hoverinfo='none'))

# Add color points for each selected group
if groups:
    for group in groups:
        group_name = group["groupName"]
        group_data = group["data"]
        
        # Determine visibility based on multi-select
        is_visible = (group_name in selected_groups)

        # Create custom hover text for each point
        hover_texts = [
            f"<b>ID:</b> {row['ID (company, number)']}<br>" +
            f"<b>Marking:</b> {row['Marking']}<br>" +
            f"<b>Group:</b> {row['Group']}<br><br>" +
            f"<b>L*:</b> {row['L']:.2f}<br>" +
            f"<b>a*:</b> {row['A']:.2f}<br>" +
            f"<b>b*:</b> {row['B']:.2f}<extra></extra>"
            for index, row in group_data.iterrows()
        ]
        
        fig.add_trace(go.Scatter3d(
            x=group_data['A'], y=group_data['B'], z=group_data['L'],
            mode='markers',
            marker=dict(size=6, opacity=0.8),
            name=f"Group {group_name}",
            visible=is_visible,
            hovertemplate=hover_texts
        ))

# --- 4. Configure Layout and Display the Plot ---
fig.update_layout(
    title_text="3D View of Color Data",
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        annotations=[
            dict(x=0, y=0, z=105, text="<b>L*</b>", showarrow=False, font=dict(size=14)),
            dict(x=110, y=0, z=50, text="<b>a*</b>", showarrow=False, font=dict(size=14)),
            dict(x=0, y=110, z=50, text="<b>b*</b>", showarrow=False, font=dict(size=14))
        ],
        camera=dict(
            projection=dict(type='orthographic')
        )
    ),
    margin=dict(r=0, l=0, b=0, t=40),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
