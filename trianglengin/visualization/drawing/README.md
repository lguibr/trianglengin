
# Visualization Drawing Submodule (`trianglengin.visualization.drawing`)

## Purpose and Architecture

This submodule contains specialized functions responsible for drawing specific visual elements of the game onto Pygame surfaces for the **interactive modes** within the `trianglengin` library. These functions are typically called by the core renderer (`Visualizer`) in [`trianglengin.visualization.core`](../core/README.md).

-   **[`grid.py`](grid.py):** Functions for drawing the grid background (`draw_grid_background`), the individual triangles within it colored based on occupancy/emptiness (`draw_grid_triangles`), and optional indices (`draw_grid_indices`).
-   **[`shapes.py`](shapes.py):** Contains `draw_shape`, a function to render a given `Shape` object at a specific location on a surface (used primarily for previews).
-   **[`previews.py`](previews.py):** Handles rendering related to shape previews:
    -   `render_previews`: Draws the dedicated preview area, including borders and the shapes within their slots, handling selection highlights.
    -   `draw_placement_preview`: Draws a semi-transparent version of a shape snapped to the grid, indicating a potential placement location (used in play mode hover).
    -   `draw_floating_preview`: Draws a semi-transparent shape directly under the mouse cursor when hovering over the grid but not snapped (used in play mode hover).
-   **[`hud.py`](hud.py):** `render_hud` draws Heads-Up Display elements like help text onto the main screen surface (simplified for interactive modes).
-   **[`highlight.py`](highlight.py):** `draw_debug_highlight` draws a distinct border around a specific triangle, used for visual feedback in debug mode.

## Exposed Interfaces

-   **Grid Drawing:**
    -   `draw_grid_background(surface: pygame.Surface, bg_color: tuple)`
    -   `draw_grid_triangles(surface: pygame.Surface, grid_data: GridData, config: EnvConfig)`
    -   `draw_grid_indices(surface: pygame.Surface, grid_data: GridData, config: EnvConfig, fonts: Dict[str, Optional[pygame.font.Font]])`
-   **Shape Drawing:**
    -   `draw_shape(surface: pygame.Surface, shape: Shape, topleft: Tuple[int, int], cell_size: float, is_selected: bool = False, origin_offset: Tuple[int, int] = (0, 0))`
-   **Preview Drawing:**
    -   `render_previews(surface: pygame.Surface, game_state: GameState, area_topleft: Tuple[int, int], mode: str, env_config: EnvConfig, vis_config: VisConfig, selected_shape_idx: int = -1) -> Dict[int, pygame.Rect]`
    -   `draw_placement_preview(surface: pygame.Surface, shape: Shape, r: int, c: int, is_valid: bool, config: EnvConfig)`
    -   `draw_floating_preview(surface: pygame.Surface, shape: Shape, screen_pos: Tuple[int, int], config: EnvConfig)`
-   **HUD Drawing:**
    -   `render_hud(surface: pygame.Surface, mode: str, fonts: Dict[str, Optional[pygame.font.Font]], display_stats: Optional[Dict[str, Any]] = None)`
-   **Highlight Drawing:**
    -   `draw_debug_highlight(surface: pygame.Surface, r: int, c: int, config: EnvConfig)`

## Dependencies

-   **[`trianglengin.visualization.core`](../core/README.md)**: `colors`, `coord_mapper`.
-   **`trianglengin.core`**: `EnvConfig`, `GameState`, `GridData`, `Shape`, `Triangle`.
-   **`alphatriangle.config`**: `VisConfig` (Imported temporarily).
-   **`pygame`**: The core library used for all drawing operations.
-   **Standard Libraries:** `typing`, `logging`, `math`.

---

**Note:** Please keep this README updated when adding new drawing functions, modifying existing ones, or changing their dependencies.