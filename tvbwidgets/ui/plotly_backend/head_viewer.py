import plotly.graph_objects as go
import numpy as np
from tvbwidgets.ui.plotly_backend.base_viewer import PlotlyBaseViewer

class HeadViewer(PlotlyBaseViewer):
    """
    3D brain surface viewer using Plotly.
    Inherits from PlotlyBaseViewer for common visualization features.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize the 3D figure
        self.fig = go.FigureWidget()
        
        # Configure 3D scene
        self.fig.update_layout(
            scene=dict(
                aspectmode='data',
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                xaxis=dict(showbackground=False),
                yaxis=dict(showbackground=False),
                zaxis=dict(showbackground=False)
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )
        
        # Enable WebGL for better performance
        self.enable_webgl()
        
        # Store mesh data
        self.meshes = {}
        
    def add_brain_surface(self, vertices, triangles, name='Brain', 
                         color='lightgray', scalars=None):
        """
        Add a brain surface mesh to the 3D viewer.
        
        Parameters:
        -----------
        vertices : np.ndarray
            Nx3 array of vertex coordinates
        triangles : np.ndarray
            Mx3 array of triangle indices
        name : str
            Name of the surface for legend
        color : str
            Color of the surface if no scalars provided
        scalars : np.ndarray, optional
            Scalar values for coloring vertices
        """
        if scalars is not None:
            # Create surface with scalar coloring
            mesh = go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=triangles[:, 0],
                j=triangles[:, 1],
                k=triangles[:, 2],
                intensity=scalars,
                colorscale='Viridis',
                opacity=1.0,
                name=name,
                showscale=True
            )
        else:
            # Create surface with solid color
            mesh = go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=triangles[:, 0],
                j=triangles[:, 1],
                k=triangles[:, 2],
                color=color,
                opacity=1.0,
                name=name
            )
        
        self.fig.add_trace(mesh)
        self.meshes[name] = mesh
        return mesh
    
    def update_surface_color(self, name, color=None, scalars=None):
        """
        Update the color of a brain surface.
        
        Parameters:
        -----------
        name : str
            Name of the surface to update
        color : str, optional
            New solid color
        scalars : np.ndarray, optional
            New scalar values for coloring
        """
        if name not in self.meshes:
            return
            
        mesh = self.meshes[name]
        if scalars is not None:
            mesh.intensity = scalars
            mesh.color = None
        elif color is not None:
            mesh.intensity = None
            mesh.color = color
    
    def set_view(self, azimuth=None, elevation=None, distance=None):
        """
        Set the camera view parameters.
        
        Parameters:
        -----------
        azimuth : float, optional
            Azimuthal angle in degrees
        elevation : float, optional
            Elevation angle in degrees
        distance : float, optional
            Camera distance from center
        """
        camera = self.fig.layout.scene.camera
        
        if azimuth is not None or elevation is not None:
            # Convert angles to radians
            azimuth = np.radians(azimuth if azimuth is not None else 0)
            elevation = np.radians(elevation if elevation is not None else 0)
            
            # Calculate camera position
            x = np.cos(elevation) * np.sin(azimuth)
            y = np.cos(elevation) * np.cos(azimuth)
            z = np.sin(elevation)
            
            # Scale by distance if provided
            if distance is not None:
                x *= distance
                y *= distance
                z *= distance
            
            camera.eye = dict(x=x, y=y, z=z)
    
    def remove_surface(self, name):
        """
        Remove a brain surface from the viewer.
        
        Parameters:
        -----------
        name : str
            Name of the surface to remove
        """
        if name in self.meshes:
            # Find and remove the trace
            for i, trace in enumerate(self.fig.data):
                if trace.name == name:
                    self.fig.data = tuple(
                        t for j, t in enumerate(self.fig.data) 
                        if j != i
                    )
                    break
            del self.meshes[name]
    
    def clear(self):
        """Clear all surfaces from the viewer."""
        self.fig.data = []
        self.meshes.clear()

    def add_transparency_slider(self, container):
        import ipywidgets as widgets

        slider = widgets.FloatSlider(
            value=1.0,
            min=0.0,
            max=1.0,
            step=0.01,
            description='Opacity:'
        )

        def on_opacity_change(change):
            for trace in self.fig.data:
                if isinstance(trace, go.Mesh3d):
                    trace.opacity = change['new']

        slider.observe(on_opacity_change, names='value')
        container.children += (slider,)

    def add_colormap_selector(self, container):
        import ipywidgets as widgets

        dropdown = widgets.Dropdown(
            options=['Viridis', 'Plasma', 'Inferno', 'RdBu', 'Spectral'],
            value='Viridis',
            description='Colormap:'
        )

        def on_colormap_change(change):
            for trace in self.fig.data:
                if isinstance(trace, go.Mesh3d):
                    trace.colorscale = change['new']

        dropdown.observe(on_colormap_change, names='value')
        container.children += (dropdown,)

    def show(self):
        """
        Display the brain visualization.
        Returns the figure for display in Jupyter.
        """
        # Ensure WebGL is enabled
        self.enable_webgl()
        
        # Add camera controls
        self.add_camera_controls()
        
        # Update layout for better interaction
        self.fig.update_layout(
            scene=dict(
                dragmode='orbit'
            )
        )
        
        display(self.fig)