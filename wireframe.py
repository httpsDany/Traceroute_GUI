import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import geodatasets

# ---------------------------
# Convert lon/lat to 3D coords
# ---------------------------
def lonlat_to_xyz(lon, lat, R=1.01):
    lon, lat = np.radians(lon), np.radians(lat)
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
    return x, y, z

# ---------------------------
# Create black occlusion sphere
# ---------------------------
def create_black_sphere(R=1, steps=100):
    u = np.linspace(0, 2*np.pi, steps)
    v = np.linspace(-np.pi/2, np.pi/2, steps)
    x = np.outer(np.cos(u), np.cos(v))
    y = np.outer(np.sin(u), np.cos(v))
    z = np.outer(np.ones_like(u), np.sin(v))

    return go.Surface(
        x=R*x, y=R*y, z=R*z,
        colorscale=[[0, "black"], [1, "black"]],
        showscale=False,
        opacity=1.0
    )

# ---------------------------
# Load Natural Earth borders
# ---------------------------
world = gpd.read_file("110m_cultural/ne_110m_admin_0_countries.shp")

fig = go.Figure()

# Add occlusion sphere first
fig.add_trace(create_black_sphere(R=1.0))

# Draw country borders as white lines slightly above sphere
for _, row in world.iterrows():
    geom = row.geometry
    if geom.geom_type == "Polygon":
        polys = [geom]
    elif geom.geom_type == "MultiPolygon":
        polys = list(geom.geoms)
    else:
        continue

    for poly in polys:
        lon, lat = poly.exterior.xy
        x, y, z = lonlat_to_xyz(lon, lat, R=1.01)  # slightly above sphere
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color="white", width=2),
            showlegend=False
        ))

# ---------------------------
# Layout styling
# ---------------------------
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        bgcolor="black"
    ),
    paper_bgcolor="black",
    margin=dict(l=0, r=0, t=0, b=0)
)

fig.show()

