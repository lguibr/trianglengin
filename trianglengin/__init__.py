"""
Triangle Engine Library (`trianglengin`)

Core components for AlphaTriangle/MuzeroTriangle projects.
"""

# Expose key components from submodules
from . import app, cli, config, core, interaction, visualization

__all__ = [
    "core",
    "config",
    "visualization",
    "interaction",
    "app",
    "cli",
]
