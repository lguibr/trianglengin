"""
Visualization module for rendering the game state using Pygame.
Provides components for interactive play/debug modes.
"""

# Import core components needed externally
# Import VisConfig from alphatriangle (assuming it stays there for training viz)
# If VisConfig moves entirely, import from .config
from alphatriangle.config import VisConfig

from ..config import EnvConfig
from .core import colors
from .core.coord_mapper import (
    get_grid_coords_from_screen,
    get_preview_index_from_screen,
)
from .core.fonts import load_fonts
from .core.layout import (
    calculate_interactive_layout,
    calculate_training_layout,  # Keep both for now
)
from .core.visualizer import Visualizer

# Import drawing functions that might be useful externally (optional)
from .drawing.grid import (
    draw_grid_background,
    draw_grid_indices,
    draw_grid_triangles,
)
from .drawing.highlight import draw_debug_highlight
from .drawing.hud import render_hud
from .drawing.previews import (
    draw_floating_preview,
    draw_placement_preview,
    render_previews,
)
from .drawing.shapes import draw_shape

__all__ = [
    # Core Renderer & Layout
    "Visualizer",
    "calculate_interactive_layout",
    "calculate_training_layout",
    "load_fonts",
    "colors",  # Export colors module
    "get_grid_coords_from_screen",
    "get_preview_index_from_screen",
    # Drawing Functions
    "draw_grid_background",
    "draw_grid_triangles",
    "draw_grid_indices",
    "draw_shape",
    "render_previews",
    "draw_placement_preview",
    "draw_floating_preview",
    "render_hud",
    "draw_debug_highlight",
    # Config (Re-exporting VisConfig from alphatriangle for now)
    "VisConfig",
    "EnvConfig",  # Re-export EnvConfig for convenience
]
