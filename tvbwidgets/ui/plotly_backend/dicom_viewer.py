import plotly.graph_objects as go
import ipywidgets as widgets
import numpy as np
from tvbwidgets.ui.plotly_backend.base_viewer import PlotlyBaseViewer

class DicomViewer(PlotlyBaseViewer):
    """
    2D DICOM slice viewer using Plotly.
    Displays slices from a 3D volume with interactive slice selection.
    """
    def __init__(self):
        super().__init__()
        
        # Initialize attributes
        self.volume = None
        self.current_slice = 0
        self.num_slices = 0
        self.window_min = 0.0
        self.window_max = 1.0

        # Create figure
        self.fig = go.FigureWidget()
        
        # Configure layout
        self.fig.update_layout(
            title='DICOM Viewer',
            width=600,
            height=600,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis=dict(
                scaleanchor="y",
                scaleratio=1,
                showgrid=False,
                zeroline=False,
                showticklabels=False
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False
            )
        )

    def set_volume(self, volume):
        """
        Set the 3D volume data and initialize the viewer.
        
        Parameters:
        -----------
        volume : np.ndarray
            3D array of shape (slices, height, width)
        """
        if not isinstance(volume, np.ndarray) or volume.ndim != 3:
            raise ValueError("Volume must be a 3D numpy array")
            
        self.volume = volume
        self.num_slices = volume.shape[0]
        self.current_slice = self.num_slices // 2  # Start at middle slice
        
        # Update the display
        self._update_slice()
        
    def set_slice(self, index):
        """
        Update the viewer to display a specific slice.
        
        Parameters:
        -----------
        index : int
            Index of the slice to display
        """
        if self.volume is None:
            return
            
        if not 0 <= index < self.num_slices:
            raise ValueError(f"Slice index must be between 0 and {self.num_slices-1}")
            
        self.current_slice = index
        self._update_slice()

    def _update_slice(self):
        """Update the displayed slice."""
        if self.volume is None:
            return

        slice_data = self.volume[self.current_slice]

        window_min = self.window_min
        window_max = self.window_max

        # Clip + normalize to [0, 1]
        clipped = np.clip(slice_data, window_min, window_max)
        normalized = (clipped - window_min) / (window_max - window_min + 1e-5)

        print("Slice shape:", normalized.shape)
        print("Slice dtype:", normalized.dtype)
        print("Window min:", window_min, "max:", window_max)
        print("Normalized min:", normalized.min(), "max:", normalized.max())

        if len(self.fig.data) == 0:
            self.fig.add_trace(
                go.Heatmap(
                    z=normalized,
                    colorscale='Gray',
                    showscale=False
                )
            )
        else:
            self.fig.data[0].z = normalized

        self.fig.update_layout(
            title=f"DICOM Viewer - Slice {self.current_slice + 1}/{self.num_slices}"
        )

    def add_slice_slider(self, container):
        """
        Add a slice selection slider to a widget container.
        
        Parameters:
        -----------
        container : ipywidgets.Widget
            Container widget to add the slider to
        """
        if self.volume is None:
            return
            
        import ipywidgets as widgets
        
        slice_slider = widgets.IntSlider(
            value=self.current_slice,
            min=0,
            max=self.num_slices - 1,
            step=1,
            description='Slice:',
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        
        def on_slice_change(change):
            self.set_slice(change['new'])
            
        slice_slider.observe(on_slice_change, names='value')
        container.children += (slice_slider,)

    def add_window_level_controls(self, container):
        import ipywidgets as widgets

        window_slider = widgets.FloatRangeSlider(
            value=[self.window_min, self.window_max],
            min=0.0,
            max=255.0,
            step=0.1,
            description='Window:',
            continuous_update=False
        )

        def on_window_change(change):
            self.window_min, self.window_max = change['new']
            self._update_slice()

        window_slider.observe(on_window_change, names='value')
        container.children += (window_slider,)

    def show(self):
        """
        Display the DICOM viewer.
        Returns the figure for display in Jupyter.
        """
        if self.volume is None:
            raise ValueError("No volume data set. Call set_volume() first.")
            
        # Enable WebGL for better performance
        self.enable_webgl()
        
        return self.fig
