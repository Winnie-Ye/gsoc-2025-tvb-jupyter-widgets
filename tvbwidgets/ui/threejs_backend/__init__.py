import plotly.graph_objects as go
import numpy as np
from tvbwidgets.ui.plotly_backend.base_viewer import PlotlyBaseViewer

class PlotlyHeadViewer(PlotlyBaseViewer):
    def __init__(self):
        super().__init__()
        self.actors = {}
        self.layout = {
            'scene': {
                'aspectmode': 'data',
                'camera': {
                    'up': dict(x=0, y=0, z=1),
                    'center': dict(x=0, y=0, z=0),
                    'eye': dict(x=1.5, y=1.5, z=1.5)
                }
            },
            'margin': dict(l=0, r=0, b=0, t=0),
            'showlegend': True
        }
        self.fig = go.Figure(layout=self.layout)
        
    def add_surface(self, vertices, triangles, name='Surface', color='lightgray', opacity=1.0):
        """Add a 3D surface mesh"""
        mesh = go.Mesh3d(
            x=vertices[:, 0],
            y=vertices[:, 1],
            z=vertices[:, 2],
            i=triangles[:, 0],
            j=triangles[:, 1],
            k=triangles[:, 2],
            name=name,
            color=color,
            opacity=opacity,
            showscale=False
        )
        self.fig.add_trace(mesh)
        self.actors[name] = mesh
        return mesh
        
    def add_points(self, points, name='Points', color='red', size=5):
        """Add 3D points (e.g., for sensors or connectivity nodes)"""
        scatter = go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            name=name,
            marker=dict(
                size=size,
                color=color,
                opacity=0.8
            )
        )
        self.fig.add_trace(scatter)
        self.actors[name] = scatter
        return scatter
        
    def add_connections(self, points, edges, weights=None, name='Connections'):
        """Add 3D connections (e.g., for connectivity edges)"""
        x, y, z = [], [], []
        
        if weights is None:
            weights = np.ones(len(edges))
            
        for idx, (i, j) in enumerate(edges):
            x.extend([points[i, 0], points[j, 0], None])
            y.extend([points[i, 1], points[j, 1], None])
            z.extend([points[i, 2], points[j, 2], None])
            
        lines = go.Scatter3d(
            x=x, y=y, z=z,
            mode='lines',
            name=name,
            line=dict(
                color=weights,
                colorscale='Viridis',
                width=2
            )
        )
        self.fig.add_trace(lines)
        self.actors[name] = lines
        return lines
        
    def show(self):
        """Display the figure"""
        self.enable_webgl()
        self.add_camera_controls()
        return self.fig
