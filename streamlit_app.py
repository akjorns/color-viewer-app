import plotly.graph_objects as go
import pandas as pd
import numpy as np

# --- Example Data Setup (replace with your real dataset) ---
np.random.seed(0)
group_data = pd.DataFrame({
    'ID (company, number)': [f"ID{i}" for i in range(1, 21)],
    'Marking': np.random.choice(['A', 'B', 'C'], 20),
    'L_star': np.random.uniform(0, 100, 20),
    'A_star': np.random.uniform(-50, 50, 20),
    'B_star': np.random.uniform(-50, 50, 20)
})
legend_label = "palette 1"
marker_colors = group_data['L_star']  # or any list of colors

# --- Hover texts ---
hover_texts = [
    f"<b>ID:</b> {row['ID (company, number)']}<br>"
    f"<b>Marking:</b> {row['Marking']}<br>"
    f"<b>palette:</b> {legend_label.replace('palette ', '')}<br><br>"
    f"<b>L*:</b> {row['L_star']:.2f}<br>"
    f"<b>a*:</b> {row['A_star']:.2f}<br>"
    f"<b>b*:</b> {row['B_star']:.2f}<extra></extra>"
    for _, row in group_data.iterrows()
]

# --- Main 3D Scatter ---
fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=group_data['A_star'],
    y=group_data['B_star'],
    z=group_data['L_star'],
    mode='markers',
    marker=dict(size=7, opacity=1.0, color=marker_colors, colorscale="Viridis"),
    name=legend_label,
    hovertemplate="%{text}",
    text=hover_texts
))

fig.update_layout(
    hoverlabel=dict(
        bgcolor="white",
        font_color="#F21578",
        bordercolor="#F21578"
    ),
    scene=dict(
        xaxis_title='A*',
        yaxis_title='B*',
        zaxis_title='L*'
    ),
    title="3D L*a*b* Scatter"
)

# --- Isolated L-axis plot ---
fig_L = go.Figure()
fig_L.add_trace(go.Scatter(
    x=group_data['L_star'],
    y=[0] * len(group_data),
    mode='markers',
    marker=dict(size=7, opacity=1.0, color=marker_colors, colorscale="Viridis"),
    text=hover_texts,
    hovertemplate="%{text}"
))
fig_L.update_layout(title="L* Axis View", xaxis_title="L*", yaxis=dict(visible=False), showlegend=False)

# --- Isolated A-axis plot ---
fig_A = go.Figure()
fig_A.add_trace(go.Scatter(
    x=group_data['A_star'],
    y=[0] * len(group_data),
    mode='markers',
    marker=dict(size=7, opacity=1.0, color=marker_colors, colorscale="Viridis"),
    text=hover_texts,
    hovertemplate="%{text}"
))
fig_A.update_layout(title="A* Axis View", xaxis_title="A*", yaxis=dict(visible=False), showlegend=False)

# --- Isolated B-axis plot ---
fig_B = go.Figure()
fig_B.add_trace(go.Scatter(
    x=group_data['B_star'],
    y=[0] * len(group_data),
    mode='markers',
    marker=dict(size=7, opacity=1.0, color=marker_colors, colorscale="Viridis"),
    text=hover_texts,
    hovertemplate="%{text}"
))
fig_B.update_layout(title="B* Axis View", xaxis_title="B*", yaxis=dict(visible=False), showlegend=False)

# --- Show all figures ---
fig.show()
fig_L.show()
fig_A.show()
fig_B.show()
