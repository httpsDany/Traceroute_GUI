import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import subprocess, re, requests
from dash import Dash, dcc, html, Input, Output

# Convert lon/lat to 3D coords
def lonlat_to_xyz(lon, lat, R=1.02):
    lon, lat = np.radians(lon), np.radians(lat)
    x = R * np.cos(lat) * np.cos(lon)
    y = R * np.cos(lat) * np.sin(lon)
    z = R * np.sin(lat)
    return x, y, z

# Create black small sphere to hide the opposite side wireframe
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
        opacity=1.0,
        hoverinfo="skip"   # disable hover on globe
    )

# Load Natural Earth borders
world = gpd.read_file("110m_cultural/ne_110m_admin_0_countries.shp")

def base_globe():
    fig = go.Figure()
    fig.add_trace(create_black_sphere(R=1.0))
    for _, row in world.iterrows():
        geom = row.geometry
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for poly in polys:
            lon, lat = poly.exterior.xy
            x, y, z = lonlat_to_xyz(lon, lat, R=1.01)
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode="lines",
                line=dict(color="white", width=2),
                showlegend=False,
                hoverinfo="skip"   # disable hover on borders
            ))
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
    return fig

# Geolocate an IP
def geolocate_ip(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = r.json()
        if data["status"] == "success":
            return data["lon"], data["lat"], data.get("city", "Unknown")
    except:
        return None
    return None

# Run traceroute & map hops
def run_traceroute_with_geo(ip_address):
    result = subprocess.run(["traceroute", "-n", ip_address],
                            capture_output=True, text=True)
    hops = []
    for line in result.stdout.splitlines()[1:]:  # skip header
        m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            hop_ip = m.group(1)
            loc = geolocate_ip(hop_ip)
            if loc:
                hops.append((hop_ip, loc))  # (ip, (lon, lat, city))
    return hops

# Great-circle helper
def great_circle_arc(lon1, lat1, lon2, lat2, n_points=50, R=1.05):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    x1, y1, z1 = np.cos(lat1)*np.cos(lon1), np.cos(lat1)*np.sin(lon1), np.sin(lat1)
    x2, y2, z2 = np.cos(lat2)*np.cos(lon2), np.cos(lat2)*np.sin(lon2), np.sin(lat2)
    dot = x1*x2 + y1*y2 + z1*z2
    omega = np.arccos(np.clip(dot, -1, 1))
    t_vals = np.linspace(0, 1, n_points)
    arc_points = []
    for t in t_vals:
        A = np.sin((1-t)*omega) / np.sin(omega)
        B = np.sin(t*omega) / np.sin(omega)
        x = A*x1 + B*x2
        y = A*y1 + B*y2
        z = A*z1 + B*z2
        norm = np.sqrt(x**2 + y**2 + z**2)
        arc_points.append((R*x/norm, R*y/norm, R*z/norm))
    return zip(*arc_points)

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Input(
            id="ip-input", type="text",
            placeholder="Enter IP address and press Enter",
            debounce=True
        ),
    ], style={"position": "absolute", "top": "10px", "right": "10px", "zIndex": "1000"}),

    dcc.Graph(id="globe", figure=base_globe(), style={"height": "100vh"})
])

@app.callback(
    Output("globe", "figure"),
    Input("ip-input", "value"),
    prevent_initial_call=True
)
def update_globe(ip_address):
    fig = base_globe()
    hops = run_traceroute_with_geo(ip_address)

    if not hops:
        return fig

    coords = []
    for idx, (ip, (lon, lat, city)) in enumerate(hops):
        x, y, z = lonlat_to_xyz(lon, lat, R=1.05)
        coords.append((lon, lat))
        color = "blue" if (idx == 0 or idx == len(hops)-1) else "red"

        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="markers",
            marker=dict(color=color, size=5, symbol="circle"),
            text=[ip],                       # used in hover
            customdata=[[city]],             # extra info
            hovertemplate="IP: %{text}<br>City: %{customdata[0]}<extra></extra>",
            showlegend=False
        ))

    # Draw great-circle arcs
    for (lon1, lat1), (lon2, lat2) in zip(coords[:-1], coords[1:]):
        arc_x, arc_y, arc_z = great_circle_arc(lon1, lat1, lon2, lat2)
        fig.add_trace(go.Scatter3d(
            x=list(arc_x), y=list(arc_y), z=list(arc_z),
            mode="lines",
            line=dict(color="red", width=2),
            showlegend=False,
            hoverinfo="skip"   # no hover for lines
        ))

    return fig

if __name__ == "__main__":
    app.run(debug=True, port=8050)

