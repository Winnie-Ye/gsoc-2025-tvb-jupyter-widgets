# tvbwidgets/ui/plotly_backend/base_viewer.py
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets


class PlotlyBaseViewer:
    def __init__(self):
        self.fig = None
        self.layout = None
        self.config = {
            'scrollZoom': True,
            'editable': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': [
                'hoverClosest3d',
                'orbitRotation',
                'resetCameraDefault3d'
            ]
        }

    def enable_webgl(self):
        """Enable WebGL rendering for better performance"""
        if self.fig is not None:
            for trace in self.fig.data:
                if hasattr(trace, 'type'):
                    if trace.type in ['scatter', 'scattergl']:
                        trace.type = 'scattergl'
                    elif trace.type in ['scatter3d', 'surface']:
                        trace.type = 'surface'

    def add_camera_controls(self):
        """Add orbit/pan/zoom controls"""
        if self.fig is not None:
            self.fig.update_layout(
                scene=dict(
                    camera=dict(
                        up=dict(x=0, y=0, z=1),
                        center=dict(x=0, y=0, z=0),
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    ),
                    dragmode='orbit'
                )
            )

    def add_transparency_slider(self, container):
        """Add opacity control slider"""
        opacity_slider = widgets.FloatSlider(
            value=1.0,
            min=0.0,
            max=1.0,
            step=0.1,
            description='Opacity:',
            continuous_update=True
        )

        def update_opacity(change):
            if self.fig is not None:
                for trace in self.fig.data:
                    trace.opacity = change['new']

        opacity_slider.observe(update_opacity, names='value')
        container.children += (opacity_slider,)

    def add_colormap_selector(self, container):
        """Add colormap selection dropdown"""
        colormaps = ['Viridis', 'Plasma', 'Inferno', 'RdBu', 'Spectral']
        colormap_dropdown = widgets.Dropdown(
            options=colormaps,
            value='Viridis',
            description='Colormap:'
        )

        def update_colormap(change):
            if self.fig is not None:
                for trace in self.fig.data:
                    if hasattr(trace, 'colorscale'):
                        trace.colorscale = change['new'].lower()

        colormap_dropdown.observe(update_colormap, names='value')
        container.children += (colormap_dropdown,)