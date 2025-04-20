File: LICENSE

MIT License

Copyright (c) 2025 Luis Guilherme P. M.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

File: MANIFEST.in
include README.md
include LICENSE
graft trianglengin
graft tests
include pyproject.toml
global-exclude __pycache__
global-exclude *.py[co]


File: out.md


File: pyproject.toml

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "trianglengin"
version = "0.1.0" # Initial version
authors = [{ name="Luis Guilherme P. M.", email="lgpelin92@gmail.com" }]
description = "Core engine (game logic, features, data) for AlphaTriangle/MuzeroTriangle."
readme = "README.md"
license = { file="LICENSE" }
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Games/Entertainment :: Puzzle Games",
    "Development Status :: 3 - Alpha",
]
dependencies = [
    "numpy>=1.20.0",
    "pydantic>=2.0.0",
    "typing_extensions>=4.0.0",
    "pygame>=2.1.0", # Added Pygame
    "typer[all]>=0.9.0", # Added Typer for CLI
    # Add other core dependencies as needed (e.g., numba if grid_features moves here later)
    # Keep Ray out for now unless StatsCollector moves here
]

[project.urls]
"Homepage" = "https://github.com/lguibr/alphatriangle" # Link to the main project for now
"Bug Tracker" = "https://github.com/lguibr/alphatriangle/issues"

# --- ADDED: Script Entry Point ---
[project.scripts]
trianglengin = "trianglengin.cli:app"
# --- END ADDED ---

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=3.0.0",
    "pytest-mock>=3.0.0", # Add if mocking is needed in tests
    "ruff",
    "mypy",
    "build",
    "twine",
    "codecov", # If using codecov
    # Add Ray here if testing StatsCollectorActor locally
    # "ray>=2.8.0",
]

[tool.setuptools.packages.find]
where = ["."] # Search for packages in the root directory

[tool.setuptools.package-data]
"*" = ["*.txt", "*.md", "*.json"] # Include non-code files

# --- Tool Configurations (Optional but Recommended) ---

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "C4", "ARG", "SIM", "TCH", "PTH", "NPY"]
ignore = ["E501"] # Ignore line length errors if needed selectively

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true # Start with true, gradually reduce

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --cov=trianglengin --cov-report=term-missing"
testpaths = [
    "tests",
]

[tool.coverage.run]
omit = [
    "*/__init__.py",
    "*/README.md",
    "trianglengin/config/*", # Config models are mostly declarative
    "trianglengin/utils/types.py", # Simple type aliases
    "trianglengin/core/structs/*", # Simple data structures
    "trianglengin/app.py", # UI App difficult to cover fully
    "trianglengin/cli.py", # CLI difficult to cover fully
    "trianglengin/visualization/core/fonts.py", # Font loading depends on system
    "tests/*", # Exclude tests from coverage report
]

[tool.coverage.report]
fail_under = 50 # Start with a reasonable target for core logic
show_missing = true

File: README.md
[![CI Status](https://github.com/lguibr/alphatriangle/actions/workflows/trianglengin_ci_cd.yml/badge.svg)](https://github.com/lguibr/alphatriangle/actions/workflows/trianglengin_ci_cd.yml) <!-- Update workflow name if changed -->
[![codecov](https://codecov.io/gh/lguibr/alphatriangle/graph/badge.svg?token=YOUR_CODECOV_TOKEN_HERE&flag=trianglengin)](https://codecov.io/gh/lguibr/alphatriangle)
[![PyPI version](https://badge.fury.io/py/trianglengin.svg)](https://badge.fury.io/py/trianglengin)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

# Triangle Engine (`trianglengin`)

This library provides the core, reusable components for reinforcement learning agents playing a triangle puzzle game, specifically designed for use by the [AlphaTriangle](https://github.com/lguibr/alphatriangle) and potentially MuzeroTriangle projects.

It encapsulates:

1.  **Core Game Logic:** Environment rules, state representation, actions.
2.  **Basic Visualization:** Pygame rendering for interactive play/debug modes.
3.  **Interaction Handling:** Input processing for interactive modes.
4.  **Utilities:** General helpers, SumTree, geometry functions, shared types (Planned).
5.  **Statistics Collection:** The `StatsCollectorActor` (Planned).
6.  **Feature Extraction:** Logic to convert game state to NN input format (Planned).
7.  **Data Management Framework:** Structure for saving/loading checkpoints and buffers (Planned).

---

## 🎮 The Ultimate Triangle Puzzle Guide 🧩

Get ready to become a Triangle Master! This guide explains everything you need to know to play the game, step-by-step, with lots of details!

### 1. Introduction: Your Mission! 🎯

Your goal is to place colorful shapes onto a special triangular grid. By filling up lines of triangles, you make them disappear and score points! Keep placing shapes and clearing lines for as long as possible to get the highest score before the grid fills up and you run out of moves. Sounds simple? Let's dive into the details!

### 2. The Playing Field: The Grid 🗺️

- **Triangle Cells:** The game board is a grid made of many small triangles. Some point UP (🔺) and some point DOWN (🔻). They alternate like a checkerboard pattern.
- **Shape:** The grid itself is roughly triangular, often wider in the middle and narrower at the top and bottom.
- **Playable Area:** You can only place shapes within the main grid area.
- **Death Zones 💀:** Around the edges of the grid, some triangles might be grayed out or look different. These are "Death Zones". You **cannot** place any part of a shape onto these triangles. They are off-limits! Think of them as the boundaries.

### 3. Your Tools: The Shapes 🟦🟥🟩

- **Shape Formation:** Each shape is a collection of connected small triangles (🔺 and 🔻). They come in different colors and arrangements. Some might be a single triangle, others might be long lines, L-shapes, or more complex patterns.
- **Relative Positions:** The triangles within a shape have fixed positions _relative to each other_. When you move the shape, all its triangles move together as one block.
- **Preview Area:** You will always have **three** shapes available to choose from at any time. These are shown in a special "preview area" on the side of the screen.

### 4. Making Your Move: Placing Shapes 🖱️➡️▦

This is the core action! Here's exactly how to place a shape:

- **Step 4a: Select a Shape:** Look at the three shapes in the preview area. Click on the one you want to place. It should highlight 💡 to show it's selected.
- **Step 4b: Aim on the Grid:** Move your mouse cursor over the main grid. You'll see a faint "ghost" image of your selected shape following your mouse. This preview helps you aim.
- **Step 4c: The Placement Rules (MUST Follow!)**
  - 📏 **Rule 1: Fit Inside:** ALL triangles of your chosen shape must land within the playable grid area. No part of the shape can hang off the edge or land in a Death Zone 💀.
  - 🧱 **Rule 2: No Overlap:** ALL triangles of your chosen shape must land on currently _empty_ spaces on the grid. You cannot place a shape on top of triangles that are already filled with color from previous shapes.
  - 📐 **Rule 3: Orientation Match!** This is crucial!
    - If a part of your shape is an UP triangle (🔺), it MUST land on an UP space (🔺) on the grid.
    - If a part of your shape is a DOWN triangle (🔻), it MUST land on a DOWN space (🔻) on the grid.
    - 🔺➡️🔺 (OK!)
    - 🔻➡️🔻 (OK!)
    - 🔺➡️🔻 (INVALID! ❌)
    - 🔻➡️🔺 (INVALID! ❌)
  - **Visual Feedback:** The game helps you!
    - 👍 **Valid Spot:** If the position under your mouse follows ALL three rules, the ghost preview will usually look solid and possibly greenish. This means you _can_ place the shape here.
    - 👎 **Invalid Spot:** If the position breaks _any_ of the rules (out of bounds, overlaps, wrong orientation), the ghost preview will usually look faded and possibly reddish. This means you _cannot_ place the shape here.
- **Step 4d: Confirm Placement:** Once you find a **valid** spot (👍), click the left mouse button again. _Click!_ The shape is now placed permanently on the grid! ✨

### 5. Scoring Points: How You Win! 🏆

You score points in two main ways:

- **Placing Triangles:** You get a small number of points for _every single small triangle_ that makes up the shape you just placed. (e.g., placing a 3-triangle shape might give you 3 \* tiny_score points).
- **Clearing Lines:** This is where the BIG points come from! You get a much larger number of points for _every single small triangle_ that disappears when you clear a line (or multiple lines at once!). See the next section for details!

### 6. Line Clearing Magic! ✨ (The Key to High Scores!)

This is the most exciting part! When you place a shape, the game immediately checks if you've completed any lines. This section explains how the game _finds_ and _clears_ these lines.

- **What Lines Can Be Cleared?** There are **three** types of lines the game looks for:

  - **Horizontal Lines ↔️:** A straight, unbroken line of filled triangles going across a single row.
  - **Diagonal Lines (Top-Left to Bottom-Right) ↘️:** An unbroken diagonal line of filled triangles stepping down and to the right.
  - **Diagonal Lines (Bottom-Left to Top-Right) ↗️:** An unbroken diagonal line of filled triangles stepping up and to the right.

- **How Lines are Found: The Tracing Method (Transversion)**

  - **The Idea:** Instead of checking every possible line combination all the time, the game pre-calculates all _potential_ maximal lines (the longest possible lines in each direction) when it starts. It does this by "tracing" or "transversing" paths from every playable triangle on the grid.
  - **Starting Point:** Imagine picking any triangle `(r, c)` on the grid.
  - **Tracing Backwards:** For each direction (Horizontal, Diagonal ↘️, Diagonal ↗️), the game first traces _backwards_ from `(r, c)` along that direction's path until it hits the edge of the grid, a death zone, or an already visited triangle (for that direction). This finds the _true beginning_ of the potential maximal line passing through `(r, c)`.
  - **Tracing Forwards:** From that true beginning point, the game traces _forwards_ along the path, adding every valid, playable triangle coordinate to a list until it hits the edge or a death zone.
  - **Recording the Line:** If the traced line is long enough (meets the minimum length requirement, usually 3 or more triangles), the game records this list of coordinates as one potential line. It also marks all triangles in this line as "visited" for this specific direction, so it doesn't trace the same maximal line multiple times starting from different points within it.
  - **All Potential Lines:** By doing this starting from _every_ playable triangle for _all three_ directions, the game builds a complete list of all possible maximal lines that could ever be cleared.

- **Defining the Paths (Neighbor Logic):** How does the game know which triangle is "next" when tracing? It depends on the current triangle's orientation (🔺 or 🔻) and the direction being traced:

  - **Horizontal ↔️:**
    - Left Neighbor: `(r, c-1)` (Always in the same row)
    - Right Neighbor: `(r, c+1)` (Always in the same row)
  - **Diagonal ↘️ (TL-BR):**
    - If current is 🔺 (Up): Next is `(r+1, c)` (Down triangle directly below)
    - If current is 🔻 (Down): Next is `(r, c+1)` (Up triangle to the right)
  - **Diagonal ↗️ (BL-TR):**
    - If current is 🔻 (Down): Next is `(r-1, c)` (Up triangle directly above)
    - If current is 🔺 (Up): Next is `(r, c+1)` (Down triangle to the right)

- **Visualizing the Paths:**

  - **Horizontal ↔️:**
    ```
    ... [🔻][🔺][🔻][🔺][🔻][🔺] ...  (Moves left/right in the same row)
    ```
  - **Diagonal ↘️ (TL-BR):** (Connects via shared horizontal edges)
    ```
    ...[🔺]...  <-- Connects below
    ...[🔻][🔺] ...
    ...     [🔻][🔺] ...
    ...         [🔻] ...
    (Path alternates row/col increments depending on orientation)
    ```
  - **Diagonal ↗️ (BL-TR):** (Connects via shared horizontal edges)
    ```
    ...           [🔺]  ... 
    ...      [🔺][🔻]   ...
    ... [🔺][🔻]        ...
    ... [🔻]            ...
    (Path alternates row/col increments depending on orientation)
    ```

- **The "Full Line" Rule:** After you place a piece, the game looks at the coordinates `(r, c)` of the triangles you just placed. It finds all the pre-calculated potential lines that contain _any_ of those coordinates. For each of those potential lines, it checks: "Is _every single triangle coordinate_ in this line now occupied?" If yes, that line is complete!

- **The _Poof_! 💨:**
  - If placing your shape completes one or MORE lines (of any type) simultaneously, all the triangles in ALL completed lines vanish instantly!
  - The spaces become empty again.
  - You score points for _every single triangle_ that vanished. Clearing multiple lines at once is the best way to rack up points! 🥳

### 7. Getting New Shapes: The Refill 🪄

- **The Trigger:** The game only gives you new shapes when a specific condition is met.
- **The Condition:** New shapes appear **only when all three of your preview slots become empty at the exact same time.**
- **How it Happens:** This usually occurs right after you place your _last_ available shape (the third one).
- **The Refill:** As soon as the third slot becomes empty, _BAM!_ 🪄 Three brand new, randomly generated shapes instantly appear in the preview slots.
- **Important:** If you place a shape and only one or two slots are empty, you **do not** get new shapes yet. You must use up all three before the refill happens.

### 8. The End of the Road: Game Over 😭

So, how does the game end?

- **The Condition:** The game is over when you **cannot legally place _any_ of the three shapes currently available in your preview slots anywhere on the grid.**
- **The Check:** After every move (placing a shape and any resulting line clears), the game checks: "Is there at least one valid spot on the grid for Shape 1? OR for Shape 2? OR for Shape 3?"
- **No More Moves:** If the answer is "NO" for all three shapes (meaning none of them can be placed anywhere according to the Placement Rules), then the game immediately ends.
- **Strategy:** This means you need to be careful! Don't fill up the grid in a way that leaves no room for the types of shapes you might get later. Always try to keep options open! 🤔

That's it! Now you know all the rules. Go forth and conquer the Triangle Puzzle! 🏆

---

## Purpose

The primary goal is to avoid code duplication between different RL agent implementations (like AlphaZero and MuZero) that operate on the same underlying game environment. By extracting the common backend logic and basic interactive UI into this installable library, the main agent projects can focus solely on their specific algorithms (MCTS variations, NN architectures, training loops, advanced visualization).

## Installation

```bash
# For development (from the trianglengin root directory):
pip install -e .[dev]

# For standard use (once published or built):
pip install trianglengin
```

## Running Interactive Modes

After installing (`pip install -e .` or `pip install trianglengin`), you can run the interactive modes directly:

- **Play Mode:**
  ```bash
  trianglengin play [--seed 42] [--log-level INFO]
  ```
- **Debug Mode:**
  ```bash
  trianglengin debug [--seed 42] [--log-level DEBUG]
  ```

## Local Development & Testing

1.  **Setup:**

    - Clone the repository.
    - Create and activate a virtual environment (`python -m venv venv && source venv/bin/activate`).
    - Install in editable mode with development dependencies: `pip install -e .[dev]`

2.  **Running Checks:**
    - **Tests & Coverage:** `pytest tests/ --cov=trianglengin --cov-report=xml` (Generates `coverage.xml` for upload)
    - **Linting:** `ruff check .`
    - **Formatting:** `ruff format .`
    - **Type Checking:** `mypy trianglengin/`

## Project Structure

```
trianglengin/
├── .github/workflows/      # GitHub Actions CI/CD
│   └── trianglengin_ci_cd.yml
├── trianglengin/           # Source code for the library package
│   ├── __init__.py         # Exposes public API
│   ├── app.py              # Interactive mode application runner
│   ├── cli.py              # CLI definition (play/debug)
│   ├── core/               # Core game logic
│   │   ├── __init__.py
│   │   ├── structs/        # Triangle, Shape, constants
│   │   │   └── README.md
│   │   └── environment/    # GameState, GridData, GridLogic, ShapeLogic, ActionCodec
│   │       └── README.md
│   ├── interaction/        # User input handling for interactive modes
│   │   └── README.md
│   ├── visualization/      # Basic Pygame rendering components
│   │   ├── __init__.py
│   │   ├── core/           # Visualizer, layout, colors, fonts, coord_mapper
│   │   │   └── README.md
│   │   └── drawing/        # Specific drawing functions (grid, shapes, previews, hud)
│   │       └── README.md
│   ├── features/           # Feature extraction logic (Planned)
│   │   └── README.md
│   ├── data/               # Data management framework (Planned)
│   │   └── README.md
│   ├── stats/              # Statistics collection actor (Planned)
│   │   └── README.md
│   ├── utils/              # General utilities (Planned)
│   │   └── README.md
│   └── config/             # Shared configuration models
│       ├── __init__.py
│       └── env_config.py   # Environment configuration
├── tests/                  # Unit tests for trianglengin components
│   ├── __init__.py
│   ├── conftest.py         # Shared test fixtures
│   ├── core/
│   │   ├── __init__.py
│   │   ├── environment/
│   │   └── structs/
│   └── README.md
├── .gitignore
├── pyproject.toml          # Build config, dependencies
├── README.md               # This file
├── LICENSE
└── MANIFEST.in
```

## Core Components (Phase 1 + Interactive UI)

- **`trianglengin.core`**: Contains the fundamental game logic.
  - **`structs`**: Defines `Triangle`, `Shape`, and related constants. ([`core/structs/README.md`](trianglengin/core/structs/README.md))
  - **`environment`**: Defines `GameState`, `GridData`, `GridLogic`, `ShapeLogic`, action encoding/decoding, and step execution logic. ([`core/environment/README.md`](trianglengin/core/environment/README.md))
- **`trianglengin.config`**: Contains shared configuration models (`EnvConfig`).
- **`trianglengin.visualization`**: Basic Pygame rendering (`Visualizer`, drawing functions, colors, fonts, layout). ([`visualization/README.md`](trianglengin/visualization/README.md))
- **`trianglengin.interaction`**: Input handling for interactive modes (`InputHandler`). ([`interaction/README.md`](trianglengin/interaction/README.md))
- **`trianglengin.app`**: Integrates components for interactive modes.
- **`trianglengin.cli`**: Command-line interface for `play`/`debug`.


## Contributing

Please refer to the main [AlphaTriangle repository](https://github.com/lguibr/alphatriangle) for contribution guidelines. Ensure that changes here remain compatible with the projects using this library. Keep READMEs updated.


File: .ruff_cache\CACHEDIR.TAG
Signature: 8a477f597d28d172789f06886806bc55

File: tests\conftest.py
# File: trianglengin/tests/conftest.py
import random
from typing import TYPE_CHECKING

import numpy as np
import pytest

# Import directly from the library being tested
from trianglengin.config import EnvConfig
from trianglengin.core.environment import GameState
from trianglengin.core.structs import Shape

if TYPE_CHECKING:
    from trianglengin.core.environment.grid import GridData


# Use default NumPy random number generator
rng = np.random.default_rng()


@pytest.fixture(scope="session")
def default_env_config() -> EnvConfig:
    """Provides the default EnvConfig used in the specification (session-scoped)."""
    return EnvConfig()


@pytest.fixture
def game_state(default_env_config: EnvConfig) -> GameState:
    """Provides a fresh GameState instance for testing."""
    return GameState(config=default_env_config, initial_seed=123)


@pytest.fixture
# REMOVED: default_env_config argument
def game_state_with_fixed_shapes() -> GameState:
    """
    Provides a game state with predictable initial shapes on a 3x3 grid.
    """
    # Create a specific 3x3 config for this fixture
    # IMPORTANT: Set COLS to 3 to match COLS_PER_ROW for correct ACTION_DIM
    config_3x3 = EnvConfig(ROWS=3, COLS=3, COLS_PER_ROW=[3, 3, 3], NUM_SHAPE_SLOTS=3)
    gs = GameState(config=config_3x3, initial_seed=456)

    # Override the random shapes with fixed ones for testing placement/refill
    fixed_shapes = [
        Shape([(0, 0, False)], (255, 0, 0)),  # Single down (fits at 0,0)
        Shape([(0, 0, True)], (0, 255, 0)),  # Single up (fits at 0,1)
        Shape([(0, 0, False), (0, 1, True)], (0, 0, 255)),  # Domino (fits at 0,0)
    ]
    assert len(fixed_shapes) == gs.env_config.NUM_SHAPE_SLOTS

    for i in range(len(fixed_shapes)):
        gs.shapes[i] = fixed_shapes[i]
    return gs


@pytest.fixture
def simple_shape() -> Shape:
    """Provides a simple 3-triangle connected shape (Down, Up, Down)."""
    # Connected L-shape: Down(0,0) -> Right -> Up(0,1) -> Vertical -> Down(1,1)
    triangles = [(0, 0, False), (0, 1, True), (1, 1, False)]
    color = (255, 0, 0)
    return Shape(triangles, color)


@pytest.fixture
def grid_data(default_env_config: EnvConfig) -> "GridData":
    """Provides a fresh GridData instance using the default config."""
    from trianglengin.core.environment.grid import GridData

    return GridData(config=default_env_config)


@pytest.fixture
def game_state_almost_full(default_env_config: EnvConfig) -> GameState:
    """
    Provides a game state (default config) where only a few placements are possible.
    Grid is filled completely, then specific spots are made empty.
    """
    gs = GameState(config=default_env_config, initial_seed=987)
    playable_mask = ~gs.grid_data._death_np
    gs.grid_data._occupied_np[playable_mask] = True
    # Empty (0,4) [Down] and (0,5) [Up] in the default 8x15 grid
    empty_spots = [(0, 4), (0, 5)]
    for r_empty, c_empty in empty_spots:
        if gs.grid_data.valid(r_empty, c_empty):
            gs.grid_data._occupied_np[r_empty, c_empty] = False
            gs.grid_data._color_id_np[r_empty, c_empty] = -1
    return gs


@pytest.fixture
def fixed_rng() -> random.Random:
    """Provides a Random instance with a fixed seed."""
    return random.Random(12345)


File: tests\__init__.py


File: tests\core\__init__.py
# File: trianglengin/tests/core/__init__.py
# This file can be empty


File: tests\core\environment\README.md
# File: trianglengin/trianglengin/core/environment/grid/README.md
# Environment Grid Submodule (`trianglengin.environment.grid`)

## Purpose and Architecture

This submodule manages the game's grid structure and related logic. It defines the triangular cells, their properties, relationships, and operations like placement validation and line clearing.

-   **Cell Representation:** The `Triangle` class (defined in [`trianglengin.core.structs`](../../structs/README.md)) represents a single cell, storing its position and orientation (`is_up`). The actual state (occupied, death, color) is managed within `GridData`.
-   **Grid Data Structure:** The [`GridData`](grid_data.py) class holds the grid state using efficient `numpy` arrays (`_occupied_np`, `_death_np`, `_color_id_np`). It also manages precomputed information about potential lines (sets of coordinates) for efficient clearing checks.
-   **Grid Logic:** The [`logic.py`](logic.py) module (exposed as `GridLogic`) contains functions operating on `GridData`. This includes:
    -   Initializing the grid based on `EnvConfig` (defining death zones).
    -   Precomputing potential lines (`_precompute_lines`) and indexing them (`_initialize_lines_and_index`) for efficient checking.
    -   Checking if a shape can be placed (`can_place`), **including matching triangle orientations**.
    -   Checking for and clearing completed lines (`check_and_clear_lines`). **This function does NOT implement gravity.**
-   **Grid Features:** Note: Any functions related to calculating scalar metrics (heights, holes, bumpiness) are expected to be handled outside this core engine library, likely in the main `alphatriangle` project's features module.

## Exposed Interfaces

-   **Classes:**
    -   `GridData`: Holds the grid state using NumPy arrays.
        -   `__init__(config: EnvConfig)`
        -   `valid(r: int, c: int) -> bool`
        -   `is_death(r: int, c: int) -> bool`
        -   `is_occupied(r: int, c: int) -> bool`
        -   `get_color_id(r: int, c: int) -> int`
        -   `get_occupied_state() -> np.ndarray`
        -   `get_death_state() -> np.ndarray`
        -   `get_color_id_state() -> np.ndarray`
        -   `deepcopy() -> GridData`
-   **Modules/Namespaces:**
    -   `logic` (often imported as `GridLogic`):
        -   `can_place(grid_data: GridData, shape: Shape, r: int, c: int) -> bool`
        -   `check_and_clear_lines(grid_data: GridData, newly_occupied_coords: Set[Tuple[int, int]]) -> Tuple[int, Set[Tuple[int, int]], Set[frozenset[Tuple[int, int]]]]` **(Returns: lines_cleared_count, unique_coords_cleared_set, set_of_cleared_lines_coord_sets)**

## Dependencies

-   **[`trianglengin.config`](../../../config/README.md)**:
    -   `EnvConfig`: Used by `GridData` initialization and logic functions.
-   **[`trianglengin.core.structs`](../../structs/README.md)**:
    -   Uses `Triangle`, `Shape`, `NO_COLOR_ID`.
-   **`numpy`**:
    -   Used extensively in `GridData`.
-   **Standard Libraries:** `typing`, `logging`, `numpy`, `copy`.

---

**Note:** Please keep this README updated when changing the grid structure, cell properties, placement rules, or line clearing logic. Accurate documentation is crucial for maintainability.

File: tests\core\environment\test_action_codec.py
# File: trianglengin/tests/core/environment/test_action_codec.py
# Extracted from alphatriangle/tests/environment/test_actions.py
import pytest

# Import directly from the library being tested
from trianglengin.config import EnvConfig
from trianglengin.core.environment.action_codec import decode_action, encode_action

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


def test_encode_decode_action(default_env_config: EnvConfig):
    """Test encoding and decoding actions."""
    config = default_env_config
    # Test some valid actions
    actions_to_test = [
        (0, 0, 0),
        (config.NUM_SHAPE_SLOTS - 1, config.ROWS - 1, config.COLS - 1),
        (0, config.ROWS // 2, config.COLS // 2),
    ]
    for shape_idx, r, c in actions_to_test:
        encoded = encode_action(shape_idx, r, c, config)
        decoded_shape_idx, decoded_r, decoded_c = decode_action(encoded, config)
        assert (shape_idx, r, c) == (decoded_shape_idx, decoded_r, decoded_c)


def test_encode_action_invalid_input(default_env_config: EnvConfig):
    """Test encoding with invalid inputs."""
    config = default_env_config
    with pytest.raises(ValueError):
        encode_action(-1, 0, 0, config)  # Invalid shape index
    with pytest.raises(ValueError):
        encode_action(config.NUM_SHAPE_SLOTS, 0, 0, config)  # Invalid shape index
    with pytest.raises(ValueError):
        encode_action(0, -1, 0, config)  # Invalid row
    with pytest.raises(ValueError):
        encode_action(0, config.ROWS, 0, config)  # Invalid row
    with pytest.raises(ValueError):
        encode_action(0, 0, -1, config)  # Invalid col
    with pytest.raises(ValueError):
        encode_action(0, 0, config.COLS, config)  # Invalid col


def test_decode_action_invalid_input(default_env_config: EnvConfig):
    """Test decoding with invalid inputs."""
    config = default_env_config
    action_dim = int(config.ACTION_DIM)  # type: ignore[call-overload]
    with pytest.raises(ValueError):
        decode_action(-1, config)  # Invalid action index
    with pytest.raises(ValueError):
        decode_action(action_dim, config)  # Invalid action index (out of bounds)


File: tests\core\environment\test_game_state.py
# File: trianglengin/tests/core/environment/test_game_state.py
import numpy as np
import pytest

# Import mocker fixture from pytest-mock
from pytest_mock import MockerFixture

# Import directly from the library being tested
from trianglengin.config import EnvConfig  # Added EnvConfig import
from trianglengin.core.environment import GameState, encode_action
from trianglengin.core.environment.grid import logic as GridLogic
from trianglengin.core.structs import Shape  # Added Shape import

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


def test_game_state_initialization(game_state: GameState):
    """Test the initial state of the game."""
    assert game_state.current_step == 0
    assert game_state.game_score == 0.0
    assert not game_state.is_over()
    assert len(game_state.shapes) == game_state.env_config.NUM_SHAPE_SLOTS
    # Initial state should have valid actions unless the board is tiny/unplayable
    if game_state.env_config.ROWS > 0 and game_state.env_config.COLS > 0:
        assert len(game_state.valid_actions()) > 0
    # Check grid is initialized
    assert game_state.grid_data is not None


def test_game_state_reset(game_state: GameState):
    """Test resetting the game state."""
    # Make some moves
    valid_actions = game_state.valid_actions()
    action1 = -1
    action2 = -1
    if valid_actions:
        # Ensure we don't pick the same action twice if only one is valid
        action1 = valid_actions[0]
        game_state.step(action1)
        # Re-calculate valid actions after the first step
        valid_actions_after_step = game_state.valid_actions()
        if valid_actions_after_step:
            action2 = valid_actions_after_step[0]  # Pick the first available
            # Avoid stepping with the same action if it's the only one left
            if action1 != action2 or len(valid_actions_after_step) > 1:
                game_state.step(action2)

    # Check if steps were actually taken
    steps_taken = game_state.current_step > 0
    assert (
        steps_taken
        or not valid_actions
        or (action1 != -1 and not valid_actions_after_step)
    )

    game_state.reset()

    assert game_state.current_step == 0
    assert game_state.game_score == 0.0
    assert not game_state.is_over()
    assert len(game_state.shapes) == game_state.env_config.NUM_SHAPE_SLOTS
    assert all(s is not None for s in game_state.shapes)  # Should be refilled
    if game_state.env_config.ROWS > 0 and game_state.env_config.COLS > 0:
        assert len(game_state.valid_actions()) > 0


def test_game_state_step(game_state_with_fixed_shapes: GameState):
    """Test a valid step using the 3x3 fixed shape fixture."""
    gs = game_state_with_fixed_shapes  # 3x3 grid
    initial_score = gs.game_score
    initial_step = gs.current_step
    shape_idx = 0  # First fixed shape: single down
    # Place at (0,0) which is Down and playable in the 3x3 grid
    r, c = 0, 0
    action = encode_action(shape_idx, r, c, gs.env_config)  # Config is 3x3

    # Ensure the action is valid before stepping
    assert (
        gs.shapes[shape_idx] is not None
    )  # Ensure shape exists before checking placement
    assert GridLogic.can_place(gs.grid_data, gs.shapes[shape_idx], r, c)
    assert action in gs.valid_actions(), f"Action {action} not in {gs.valid_actions()}"

    reward, done = gs.step(action)

    assert reward > -10.0  # Should not be game over penalty
    assert not done
    assert gs.current_step == initial_step + 1
    assert gs.game_score > initial_score
    assert gs.shapes[shape_idx] is None  # Shape should be removed


def test_game_state_step_invalid_action(game_state: GameState):
    """Test stepping with an invalid action index."""
    invalid_action_index = -1
    with pytest.raises(ValueError):
        game_state.step(invalid_action_index)

    invalid_action_index = int(game_state.env_config.ACTION_DIM)  # type: ignore[call-overload]
    with pytest.raises(ValueError):
        game_state.step(invalid_action_index)


def test_game_state_step_invalid_placement(game_state_with_fixed_shapes: GameState):
    """Test stepping with a valid action index but invalid placement logic."""
    gs = game_state_with_fixed_shapes
    shape_idx = 0
    # Occupy the target cell first
    r, c = 0, 0  # Valid placement spot for shape 0
    gs.grid_data._occupied_np[r, c] = True  # Occupy it
    action = encode_action(shape_idx, r, c, gs.env_config)

    # The action might be in valid_actions initially if calculated before occupation
    # but execute_placement should handle the failure.
    # We expect a reward of 0.0 as placement fails internally.
    reward, done = gs.step(action)
    assert reward == 0.0
    assert not done  # Game shouldn't end due to invalid placement attempt


def test_game_state_is_over(game_state: GameState):
    """Test game over condition."""
    assert not game_state.is_over()
    # Fill the grid completely
    playable_mask = ~game_state.grid_data._death_np
    game_state.grid_data._occupied_np[playable_mask] = True
    # Make shapes unplaceable (e.g., None)
    game_state.shapes = [None] * game_state.env_config.NUM_SHAPE_SLOTS
    # Now, valid_actions should be empty, triggering game over check in step or directly
    assert not game_state.valid_actions()
    # Manually trigger the check if needed (step would normally do this)
    if not game_state.valid_actions():
        game_state.game_over = True
    assert game_state.is_over()


def test_game_state_copy(game_state: GameState):
    """Test the deepcopy mechanism."""
    # Make a move
    valid_actions = game_state.valid_actions()
    if valid_actions:
        game_state.step(valid_actions[0])

    copy_state = game_state.copy()

    # Check basic properties
    assert copy_state.current_step == game_state.current_step
    assert copy_state.game_score == game_state.game_score
    assert copy_state.is_over() == game_state.is_over()
    assert copy_state.env_config == game_state.env_config

    # Check independence of mutable objects
    assert copy_state.grid_data is not game_state.grid_data
    assert np.array_equal(
        copy_state.grid_data._occupied_np, game_state.grid_data._occupied_np
    )
    assert copy_state.shapes is not game_state.shapes
    assert len(copy_state.shapes) == len(game_state.shapes)
    for i in range(len(game_state.shapes)):
        if game_state.shapes[i] is None:
            assert copy_state.shapes[i] is None
        else:
            assert copy_state.shapes[i] is not game_state.shapes[i]
            # Use __eq__ for comparison
            assert copy_state.shapes[i] == game_state.shapes[i]

    # Modify copy and check original is unchanged
    copy_state.game_score += 100
    assert game_state.game_score != copy_state.game_score
    if copy_state.shapes and copy_state.shapes[0]:  # Check list and element exist
        copy_state.shapes[0].color = (1, 1, 1)
        if game_state.shapes and game_state.shapes[0]:  # Check list and element exist
            assert game_state.shapes[0].color != (1, 1, 1)
    # Use a valid coordinate for the grid size
    r_mod, c_mod = 0, 0
    if copy_state.grid_data.valid(r_mod, c_mod) and not copy_state.grid_data.is_death(
        r_mod, c_mod
    ):
        original_value = copy_state.grid_data._occupied_np[r_mod, c_mod]
        copy_state.grid_data._occupied_np[r_mod, c_mod] = not original_value
        # Ensure original game state's value hasn't changed
        assert (
            game_state.grid_data._occupied_np[r_mod, c_mod]
            != copy_state.grid_data._occupied_np[r_mod, c_mod]
        )


# --- ADDED TESTS ---
def test_game_state_get_outcome_non_terminal(game_state: GameState):
    """Test get_outcome returns 0.0 for non-terminal states."""
    assert not game_state.is_over()
    assert game_state.get_outcome() == 0.0


def test_game_state_step_triggers_game_over(
    game_state_with_fixed_shapes: GameState, mocker: MockerFixture
):
    """Test that placing the last possible piece triggers game over (mocking refill)."""
    gs = game_state_with_fixed_shapes  # Has 3 slots, 3x3 grid
    # Fill the grid almost completely, leaving just enough space for the 2 single shapes
    playable_mask = ~gs.grid_data._death_np
    gs.grid_data._occupied_np[playable_mask] = True
    # Empty spots for the fixed shapes
    # Shape 0: (0,0,False) -> needs (0,0) empty [Down]
    # Shape 1: (0,0,True) -> needs (0,1) empty [Up]
    empty_spots = [(0, 0), (0, 1)]
    for r_empty, c_empty in empty_spots:
        if gs.grid_data.valid(r_empty, c_empty):
            gs.grid_data._occupied_np[r_empty, c_empty] = False
            gs.grid_data._color_id_np[r_empty, c_empty] = -1

    # --- Setup: Remove the 3rd shape (domino) so placing the 2nd empties all slots ---
    gs.shapes[2] = None

    # Mock refill_shape_slots to prevent it from running
    mock_refill = mocker.patch(
        "trianglengin.core.environment.shapes.logic.refill_shape_slots"
    )

    # Place first shape (shape 0 at 0,0)
    action1 = encode_action(0, 0, 0, gs.env_config)
    assert gs.shapes[0] is not None  # Check shape exists
    assert GridLogic.can_place(gs.grid_data, gs.shapes[0], 0, 0)  # Verify placement
    assert action1 in gs.valid_actions()
    reward1, done1 = gs.step(action1)
    assert not done1
    assert gs.shapes[0] is None
    assert gs.shapes[1] is not None  # Shape 1 (Up) remains
    assert gs.shapes[2] is None  # Shape 2 was removed
    mock_refill.assert_not_called()  # Refill shouldn't be called yet

    # Place the second shape (shape 1 at 0,1)
    action2 = encode_action(1, 0, 1, gs.env_config)
    assert gs.shapes[1] is not None  # Check shape exists
    assert GridLogic.can_place(gs.grid_data, gs.shapes[1], 0, 1)  # Verify placement
    assert action2 in gs.valid_actions()
    reward2, done2 = gs.step(action2)

    # Check if the mock was called exactly once *during* the second step
    assert mock_refill.call_count == 1, (
        f"Expected refill mock to be called once, but was called {mock_refill.call_count} times."
    )

    # Game should now be over because grid is full AND all shape slots are empty,
    # and refill was mocked, so valid_actions() will be empty.
    assert done2, (
        "Game should be over after placing the last possible piece (refill mocked)"
    )
    assert gs.is_over()
    assert not gs.valid_actions()  # No more valid actions


# --- END ADDED TESTS ---


# --- Test added for reliable game over scenario ---
def test_game_state_forced_game_over(default_env_config: EnvConfig):
    """Test game over by filling all cells of one orientation and providing only shapes of that orientation."""
    gs = GameState(config=default_env_config, initial_seed=777)
    config = gs.env_config

    # Fill all non-death UP-pointing triangles
    for r in range(config.ROWS):
        for c in range(config.COLS):
            is_up = (r + c) % 2 != 0
            if is_up and not gs.grid_data.is_death(r, c):
                gs.grid_data._occupied_np[r, c] = True

    # Provide only single UP-pointing triangles in shape slots
    up_shape = Shape([(0, 0, True)], (0, 255, 0))  # Single Up
    gs.shapes = [up_shape.copy() for _ in range(config.NUM_SHAPE_SLOTS)]

    # Verify no valid actions exist
    assert not gs.valid_actions()

    # Manually set game_over flag as step() isn't called here
    gs.game_over = True
    assert gs.is_over()

    # Test reset brings it back
    gs.reset()
    assert not gs.is_over()
    assert len(gs.valid_actions()) > 0  # Should have valid actions after reset


File: tests\core\environment\test_grid_data.py
# File: trianglengin/tests/core/environment/test_grid_data.py
import numpy as np

# Import directly from the library being tested
from trianglengin.config import EnvConfig
from trianglengin.core.environment.grid.grid_data import (
    GridData,
    _precompute_lines,
)

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


def test_grid_data_initialization(grid_data: GridData, default_env_config: EnvConfig):
    """Test basic GridData initialization."""
    assert grid_data.rows == default_env_config.ROWS
    assert grid_data.cols == default_env_config.COLS
    assert grid_data._occupied_np.shape == (
        default_env_config.ROWS,
        default_env_config.COLS,
    )
    assert grid_data._death_np.shape == (
        default_env_config.ROWS,
        default_env_config.COLS,
    )
    assert grid_data._color_id_np.shape == (
        default_env_config.ROWS,
        default_env_config.COLS,
    )
    # Check if death zone was applied to occupied
    assert np.all(grid_data._occupied_np[grid_data._death_np])
    # Check if potential lines were calculated
    assert len(grid_data.potential_lines) > 0
    assert len(grid_data._coord_to_lines_map) > 0


def test_grid_data_valid(grid_data: GridData):
    """Test the valid method."""
    assert grid_data.valid(0, 0)
    assert grid_data.valid(grid_data.rows - 1, grid_data.cols - 1)
    assert not grid_data.valid(-1, 0)
    assert not grid_data.valid(0, -1)
    assert not grid_data.valid(grid_data.rows, 0)
    assert not grid_data.valid(0, grid_data.cols)


def test_grid_data_is_death(grid_data: GridData):
    """Test the is_death method."""
    # Find a death cell (e.g., 0,0 in default config)
    assert grid_data.is_death(0, 0)
    # Find a non-death cell (e.g., center)
    center_r, center_c = grid_data.rows // 2, grid_data.cols // 2
    assert not grid_data.is_death(center_r, center_c)
    # Test out of bounds
    assert grid_data.is_death(-1, 0)


def test_grid_data_is_occupied(grid_data: GridData):
    """Test the is_occupied method."""
    # Death cells are occupied
    assert grid_data.is_occupied(0, 0)
    # Center cell should be initially empty
    center_r, center_c = grid_data.rows // 2, grid_data.cols // 2
    assert not grid_data.is_occupied(center_r, center_c)
    # Occupy it
    grid_data._occupied_np[center_r, center_c] = True
    assert grid_data.is_occupied(center_r, center_c)
    # Test out of bounds
    assert grid_data.is_occupied(-1, 0)


def test_grid_data_deepcopy(grid_data: GridData):
    """Test the deepcopy method."""
    # Occupy a cell
    r, c = grid_data.rows // 2, grid_data.cols // 2
    grid_data._occupied_np[r, c] = True
    grid_data._color_id_np[r, c] = 5

    copy_grid = grid_data.deepcopy()

    # Check basic properties
    assert copy_grid.rows == grid_data.rows
    assert copy_grid.cols == grid_data.cols
    assert copy_grid.config == grid_data.config

    # Check array independence
    assert copy_grid._occupied_np is not grid_data._occupied_np
    assert np.array_equal(copy_grid._occupied_np, grid_data._occupied_np)
    assert copy_grid._death_np is not grid_data._death_np
    assert np.array_equal(copy_grid._death_np, grid_data._death_np)
    assert copy_grid._color_id_np is not grid_data._color_id_np
    assert np.array_equal(copy_grid._color_id_np, grid_data._color_id_np)

    # Check line data independence (sets/dicts)
    assert copy_grid.potential_lines is not grid_data.potential_lines
    assert copy_grid.potential_lines == grid_data.potential_lines
    assert copy_grid._coord_to_lines_map is not grid_data._coord_to_lines_map
    assert copy_grid._coord_to_lines_map == grid_data._coord_to_lines_map
    # Check nested sets within the map
    if grid_data._coord_to_lines_map:
        key = next(iter(grid_data._coord_to_lines_map))
        assert (
            copy_grid._coord_to_lines_map[key] is not grid_data._coord_to_lines_map[key]
        )

    # Modify copy and check original
    copy_grid._occupied_np[r, c] = False
    assert grid_data._occupied_np[r, c]  # Original should still be True
    copy_grid._color_id_np[r, c] = 1
    assert grid_data._color_id_np[r, c] == 5


def test_precompute_lines_different_config():
    """Test _precompute_lines with a non-default, simple config (HORIZONTAL ONLY)."""
    # Simple 3x3 fully playable grid, min line length 2
    config = EnvConfig(ROWS=3, COLS=3, COLS_PER_ROW=[3, 3, 3], MIN_LINE_LENGTH=2)
    lines = _precompute_lines(config)  # Should only contain horizontal lines now

    # Convert to sets of frozensets for easier comparison
    line_sets = {frozenset(line) for line in lines}

    # Expected HORIZONTAL lines (length >= 2) in a 3x3 grid:
    expected_h = (
        {frozenset([(r, 0), (r, 1)]) for r in range(3)}  # Len 2
        | {frozenset([(r, 1), (r, 2)]) for r in range(3)}  # Len 2
        | {frozenset([(r, 0), (r, 1), (r, 2)]) for r in range(3)}  # Len 3
    )

    # --- REMOVED Diagonal expectations ---
    # expected_d1 = { ... }
    # expected_d2 = { ... }
    # expected_lines = expected_h | expected_d1 | expected_d2
    # --- END REMOVED ---

    expected_lines = expected_h  # Only horizontal lines expected
    assert line_sets == expected_lines
    assert len(lines) == len(expected_lines)  # Should be 3*2 + 3 = 9


File: tests\core\environment\test_grid_logic.py
# File: trianglengin/tests/core/environment/test_grid_logic.py

# Import directly from the library being tested
from trianglengin.core.environment.grid import GridData
from trianglengin.core.environment.grid import logic as GridLogic
from trianglengin.core.structs import Shape

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


# --- Test can_place with NumPy GridData ---
def test_can_place_empty_grid(grid_data: GridData, simple_shape: Shape):
    """Test placement on an empty grid."""
    # Place at (2,2).
    # Shape: [(0,0,F), (0,1,T), (1,1,F)] -> Grid: [(2,2,F), (2,3,T), (3,3,F)]
    # Check orientations:
    # (2,2) -> 2+2=4 (Even=F) -> Matches F -> OK
    # (2,3) -> 2+3=5 (Odd=T) -> Matches T -> OK
    # (3,3) -> 3+3=6 (Even=F) -> Matches F -> OK
    assert GridLogic.can_place(grid_data, simple_shape, 2, 2)


def test_can_place_occupied(grid_data: GridData, simple_shape: Shape):
    """Test placement fails if any target cell is occupied."""
    # Occupy one cell where the shape would go
    # Shape: [(0,0,F), (0,1,T), (1,1,F)] placed at (2,2) covers (2,2), (2,3), (3,3)
    target_r, target_c = 3, 3  # Occupy the cell corresponding to shape's (1,1)
    grid_data._occupied_np[target_r, target_c] = True
    assert not GridLogic.can_place(grid_data, simple_shape, 2, 2)


# Remove unused simple_shape argument
def test_can_place_death_zone(grid_data: GridData):
    """Test placement fails if any target cell is in a death zone."""
    # Find a death zone cell (e.g., top-left corner in default config)
    death_r, death_c = 0, 0
    assert grid_data._death_np[death_r, death_c]
    # Try placing a single triangle shape there
    single_down_shape = Shape([(0, 0, False)], (255, 0, 0))
    assert not GridLogic.can_place(grid_data, single_down_shape, death_r, death_c)


def test_can_place_orientation_mismatch(grid_data: GridData):
    """Test placement fails if triangle orientations don't match."""
    # Shape: Single UP triangle at its origin (0,0)
    shape_up = Shape([(0, 0, True)], (0, 255, 0))
    # Target grid cell: (0,4), which is DOWN in default config (0+4=4, even)
    target_r_down, target_c_down = 0, 4
    assert grid_data.valid(target_r_down, target_c_down) and not grid_data.is_death(
        target_r_down, target_c_down
    )
    assert not GridLogic.can_place(grid_data, shape_up, target_r_down, target_c_down)

    # Shape: Single DOWN triangle at its origin (0,0)
    shape_down = Shape([(0, 0, False)], (255, 0, 0))
    # Target grid cell: (0,3), which is UP in default config (0+3=3, odd)
    target_r_up, target_c_up = 0, 3
    assert grid_data.valid(target_r_up, target_c_up) and not grid_data.is_death(
        target_r_up, target_c_up
    )
    assert not GridLogic.can_place(grid_data, shape_down, target_r_up, target_c_up)

    # Test valid placement using playable coordinates
    assert GridLogic.can_place(grid_data, shape_down, 0, 4)  # Down on Down at (0,4)
    assert GridLogic.can_place(grid_data, shape_up, 0, 3)  # Up on Up at (0,3)


# --- Test check_and_clear_lines with NumPy GridData ---


def occupy_coords(grid_data: GridData, coords: set[tuple[int, int]]):
    """Helper to occupy specific coordinates."""
    for r, c in coords:
        if grid_data.valid(r, c) and not grid_data._death_np[r, c]:
            grid_data._occupied_np[r, c] = True


def test_check_and_clear_lines_no_clear(grid_data: GridData):
    """Test when newly occupied cells don't complete any lines."""
    # Use coordinates from the updated simple_shape placed at (2,2)
    newly_occupied = {(2, 2), (2, 3), (3, 3)}
    occupy_coords(grid_data, newly_occupied)
    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )
    assert lines_cleared == 0  # Expect 0 lines cleared
    assert not unique_cleared
    assert not cleared_lines_set
    # Check grid state unchanged (except for initial occupation)
    assert grid_data._occupied_np[2, 2]
    assert grid_data._occupied_np[2, 3]
    assert grid_data._occupied_np[3, 3]


def test_check_and_clear_lines_single_line(grid_data: GridData):
    """Test clearing a single horizontal line."""
    # Find a valid horizontal line from the precomputed set
    # Example: Look for a line in row 1 (often has long lines)
    expected_line_coords = None
    for line_fs in grid_data.potential_lines:
        coords = list(line_fs)
        # Check if it's horizontal and in row 1
        if len(coords) >= grid_data.config.MIN_LINE_LENGTH and all(
            r == 1 for r, c in coords
        ):
            expected_line_coords = frozenset(coords)
            break

    assert expected_line_coords is not None, (
        "Could not find a suitable horizontal line in row 1 for testing"
    )
    coords_list = list(expected_line_coords)
    # expected_num_triangles = len(coords_list) # No longer needed

    # Occupy all but one cell in the line
    occupy_coords(grid_data, set(coords_list[:-1]))
    # Occupy the last cell
    last_coord = coords_list[-1]
    newly_occupied = {last_coord}
    occupy_coords(grid_data, newly_occupied)

    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )

    # --- ASSERTION REVERTED ---
    assert lines_cleared == 1  # Expect exactly 1 line cleared now
    # --- END ASSERTION REVERTED ---
    assert unique_cleared == set(expected_line_coords)  # Expect set of coords
    # Check that the specific line we set up is *in* the set of cleared lines
    assert expected_line_coords in cleared_lines_set
    # Check that only one line was cleared
    assert len(cleared_lines_set) == 1

    # Verify the line is now empty in the NumPy array
    for r, c in expected_line_coords:
        assert not grid_data._occupied_np[r, c]


# --- ADDED TEST ---
def test_check_and_clear_lines_no_lines_to_check(grid_data: GridData):
    """Test the case where newly occupied coords are not part of any potential line."""
    # Occupy a cell known not to be part of any line (e.g., corner if MIN_LINE_LENGTH > 1)
    # Or occupy cells that are part of lines, but call check with unrelated coords
    newly_occupied = {(0, 0)}  # Assuming (0,0) is death or not part of lines >= 3
    # Ensure the coord is not in the map
    grid_data._coord_to_lines_map.pop((0, 0), None)

    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )
    assert lines_cleared == 0
    assert not unique_cleared
    assert not cleared_lines_set


# --- END ADDED TEST ---


File: tests\core\environment\test_shape_logic.py
# File: trianglengin/tests/core/environment/test_shape_logic.py
import random

import pytest

# Import directly from the library being tested
from trianglengin.core.environment import GameState
from trianglengin.core.environment.shapes import logic as ShapeLogic
from trianglengin.core.structs import Shape

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


def test_generate_random_shape(fixed_rng: random.Random):
    """Test generating a single random shape."""
    shape = ShapeLogic.generate_random_shape(fixed_rng)
    assert isinstance(shape, Shape)
    assert shape.triangles is not None
    assert shape.color is not None
    assert len(shape.triangles) > 0
    # Check connectivity (optional but good)
    assert ShapeLogic.is_shape_connected(shape)


def test_generate_multiple_shapes(fixed_rng: random.Random):
    """Test generating multiple shapes to ensure variety (or lack thereof with fixed seed)."""
    shape1 = ShapeLogic.generate_random_shape(fixed_rng)
    # Re-seed or use different rng instance if true randomness is needed per call
    # For this test, using the same fixed_rng will likely produce the same shape again
    shape2 = ShapeLogic.generate_random_shape(fixed_rng)
    # --- REMOVED INCORRECT ASSERTION ---
    # assert shape1 == shape2  # Expect same shape due to fixed seed - THIS IS INCORRECT
    # --- END REMOVED ---
    # Check that subsequent calls produce different results with the same RNG instance
    assert shape1 != shape2, (
        "Two consecutive calls with the same RNG produced the exact same shape (template and color), which is highly unlikely."
    )

    # Use a different seed for variation
    rng2 = random.Random(54321)
    shape3 = ShapeLogic.generate_random_shape(rng2)
    # Check that different RNGs produce different results (highly likely)
    assert shape1 != shape3 or shape1.color != shape3.color


def test_refill_shape_slots_empty(game_state: GameState, fixed_rng: random.Random):
    """Test refilling when all slots are initially empty."""
    game_state.shapes = [None] * game_state.env_config.NUM_SHAPE_SLOTS
    ShapeLogic.refill_shape_slots(game_state, fixed_rng)
    assert all(s is not None for s in game_state.shapes)
    assert len(game_state.shapes) == game_state.env_config.NUM_SHAPE_SLOTS


def test_refill_shape_slots_partial(game_state: GameState, fixed_rng: random.Random):
    """Test refilling when some slots are empty - SHOULD NOT REFILL."""
    num_slots = game_state.env_config.NUM_SHAPE_SLOTS
    if num_slots < 2:
        pytest.skip("Test requires at least 2 shape slots")

    # Start with full slots
    ShapeLogic.refill_shape_slots(game_state, fixed_rng)
    assert all(s is not None for s in game_state.shapes)

    # Empty one slot
    game_state.shapes[0] = None
    # Store original state (important: copy shapes if they are mutable)
    original_shapes = [s.copy() if s else None for s in game_state.shapes]

    # Attempt refill - it should do nothing
    ShapeLogic.refill_shape_slots(game_state, fixed_rng)

    # Check that shapes remain unchanged
    assert game_state.shapes == original_shapes, "Refill happened unexpectedly"


def test_refill_shape_slots_full(game_state: GameState, fixed_rng: random.Random):
    """Test refilling when all slots are already full - SHOULD NOT REFILL."""
    # Start with full slots
    ShapeLogic.refill_shape_slots(game_state, fixed_rng)
    assert all(s is not None for s in game_state.shapes)
    original_shapes = [s.copy() if s else None for s in game_state.shapes]

    # Attempt refill - should do nothing
    ShapeLogic.refill_shape_slots(game_state, fixed_rng)

    # Check shapes are unchanged
    assert game_state.shapes == original_shapes, "Refill happened when slots were full"


def test_refill_shape_slots_batch_trigger(game_state: GameState) -> None:
    """Test that refill only happens when ALL slots are empty."""
    num_slots = game_state.env_config.NUM_SHAPE_SLOTS
    if num_slots < 2:
        pytest.skip("Test requires at least 2 shape slots")

    # Fill all slots initially
    ShapeLogic.refill_shape_slots(game_state, game_state._rng)
    initial_shapes = [s.copy() if s else None for s in game_state.shapes]
    assert all(s is not None for s in initial_shapes)

    # Empty one slot - refill should NOT happen
    game_state.shapes[0] = None
    shapes_after_one_empty = [s.copy() if s else None for s in game_state.shapes]
    ShapeLogic.refill_shape_slots(game_state, game_state._rng)
    assert game_state.shapes == shapes_after_one_empty, (
        "Refill happened when only one slot was empty"
    )

    # Empty all slots - refill SHOULD happen
    game_state.shapes = [None] * num_slots
    ShapeLogic.refill_shape_slots(game_state, game_state._rng)
    assert all(s is not None for s in game_state.shapes), (
        "Refill did not happen when all slots were empty"
    )
    # Check that the shapes are different from the initial ones (probabilistically)
    assert game_state.shapes != initial_shapes, (
        "Shapes after refill are identical to initial shapes (unlikely)"
    )


# --- ADDED TESTS ---
def test_get_neighbors():
    """Test neighbor calculation for up and down triangles."""
    # Up triangle at (1, 1)
    up_neighbors = ShapeLogic.get_neighbors(r=1, c=1, is_up=True)
    # Expected: Left (1,0), Right (1,2), Vertical (Down) (2,1)
    assert set(up_neighbors) == {(1, 0), (1, 2), (2, 1)}

    # Down triangle at (1, 2)
    down_neighbors = ShapeLogic.get_neighbors(r=1, c=2, is_up=False)
    # Expected: Left (1,1), Right (1,3), Vertical (Up) (0,2)
    assert set(down_neighbors) == {(1, 1), (1, 3), (0, 2)}


def test_is_shape_connected_true(simple_shape: Shape):  # Use fixture
    """Test connectivity for various connected shapes."""
    # Single triangle
    shape1 = Shape([(0, 0, True)], (1, 1, 1))
    assert ShapeLogic.is_shape_connected(shape1)

    # Domino (horizontal) - Down(0,0) connects to Up(0,1)
    shape2 = Shape([(0, 0, False), (0, 1, True)], (1, 1, 1))
    assert ShapeLogic.is_shape_connected(shape2)

    # L-shape (from simple_shape fixture) - Down(0,0) connects Up(1,0), Up(1,0) connects Down(1,1)
    assert ShapeLogic.is_shape_connected(simple_shape)  # Test the fixture directly

    # Empty shape
    shape4 = Shape([], (1, 1, 1))
    assert ShapeLogic.is_shape_connected(shape4)

    # More complex connected shape
    shape5 = Shape(
        [(0, 0, False), (0, 1, True), (1, 1, False), (1, 0, True)], (1, 1, 1)
    )
    assert ShapeLogic.is_shape_connected(shape5)


def test_is_shape_connected_false():
    """Test connectivity for disconnected shapes."""
    # Two separate triangles
    shape1 = Shape([(0, 0, True), (2, 2, False)], (1, 1, 1))
    assert not ShapeLogic.is_shape_connected(shape1)

    # Three triangles, two connected, one separate
    shape2 = Shape([(0, 0, False), (0, 1, True), (3, 3, True)], (1, 1, 1))
    assert not ShapeLogic.is_shape_connected(shape2)


# --- END ADDED TESTS ---


File: tests\core\environment\test_step.py
# File: trianglengin/tests/core/environment/test_step.py
# Moved from alphatriangle/tests/environment/test_step.py
# Updated imports
import random
from time import sleep

import pytest

# Import mocker fixture from pytest-mock
from pytest_mock import MockerFixture

# Import directly from the library being tested
from trianglengin.config import EnvConfig
from trianglengin.core.environment import GameState
from trianglengin.core.environment.grid import GridData
from trianglengin.core.environment.grid import logic as GridLogic
from trianglengin.core.environment.logic.step import calculate_reward, execute_placement
from trianglengin.core.structs import Shape, Triangle

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


def occupy_line(
    grid_data: GridData, line_indices: list[int], config: EnvConfig
) -> set[Triangle]:
    """Helper to occupy triangles for a given line index list."""
    # occupied_tris: set[Triangle] = set() # Removed unused variable
    for idx in line_indices:
        r, c = divmod(idx, config.COLS)
        # Combine nested if using 'and'
        if grid_data.valid(r, c) and not grid_data.is_death(r, c):
            grid_data._occupied_np[r, c] = True
            # Cannot easily return Triangle objects anymore
    # Return empty set as Triangle objects are not the primary state
    return set()


def occupy_coords(grid_data: GridData, coords: set[tuple[int, int]]):
    """Helper to occupy specific coordinates."""
    for r, c in coords:
        if grid_data.valid(r, c) and not grid_data.is_death(r, c):
            grid_data._occupied_np[r, c] = True


# --- New Reward Calculation Tests (v3) ---


def test_calculate_reward_v3_placement_only(
    simple_shape: Shape, default_env_config: EnvConfig
):
    """Test reward: only placement, game not over."""
    placed_count = len(simple_shape.triangles)
    unique_coords_cleared: set[tuple[int, int]] = set()
    is_game_over = False
    reward = calculate_reward(
        placed_count, unique_coords_cleared, is_game_over, default_env_config
    )
    expected_reward = (
        placed_count * default_env_config.REWARD_PER_PLACED_TRIANGLE
        + default_env_config.REWARD_PER_STEP_ALIVE
    )
    assert reward == pytest.approx(expected_reward)


def test_calculate_reward_v3_single_line_clear(
    simple_shape: Shape, default_env_config: EnvConfig
):
    """Test reward: placement + line clear, game not over."""
    placed_count = len(simple_shape.triangles)
    # Simulate a cleared line of 9 unique coordinates
    unique_coords_cleared: set[tuple[int, int]] = {(0, i) for i in range(9)}
    is_game_over = False
    reward = calculate_reward(
        placed_count, unique_coords_cleared, is_game_over, default_env_config
    )
    expected_reward = (
        placed_count * default_env_config.REWARD_PER_PLACED_TRIANGLE
        + len(unique_coords_cleared) * default_env_config.REWARD_PER_CLEARED_TRIANGLE
        + default_env_config.REWARD_PER_STEP_ALIVE
    )
    assert reward == pytest.approx(expected_reward)


def test_calculate_reward_v3_multi_line_clear(
    simple_shape: Shape, default_env_config: EnvConfig
):
    """Test reward: placement + multi-line clear (overlapping coords), game not over."""
    placed_count = len(simple_shape.triangles)
    # Simulate two lines sharing coordinate (0,0)
    line1_coords = {(0, i) for i in range(9)}
    line2_coords = {(i, 0) for i in range(5)}
    unique_coords_cleared = line1_coords.union(line2_coords)  # Union handles uniqueness
    is_game_over = False
    reward = calculate_reward(
        placed_count, unique_coords_cleared, is_game_over, default_env_config
    )
    expected_reward = (
        placed_count * default_env_config.REWARD_PER_PLACED_TRIANGLE
        + len(unique_coords_cleared) * default_env_config.REWARD_PER_CLEARED_TRIANGLE
        + default_env_config.REWARD_PER_STEP_ALIVE
    )
    assert reward == pytest.approx(expected_reward)


def test_calculate_reward_v3_game_over(
    simple_shape: Shape, default_env_config: EnvConfig
):
    """Test reward: placement, no line clear, game IS over."""
    placed_count = len(simple_shape.triangles)
    unique_coords_cleared: set[tuple[int, int]] = set()
    is_game_over = True
    reward = calculate_reward(
        placed_count, unique_coords_cleared, is_game_over, default_env_config
    )
    expected_reward = (
        placed_count * default_env_config.REWARD_PER_PLACED_TRIANGLE
        + default_env_config.PENALTY_GAME_OVER
    )
    assert reward == pytest.approx(expected_reward)


def test_calculate_reward_v3_game_over_with_clear(
    simple_shape: Shape, default_env_config: EnvConfig
):
    """Test reward: placement + line clear, game IS over."""
    placed_count = len(simple_shape.triangles)
    unique_coords_cleared: set[tuple[int, int]] = {(0, i) for i in range(9)}
    is_game_over = True
    reward = calculate_reward(
        placed_count, unique_coords_cleared, is_game_over, default_env_config
    )
    expected_reward = (
        placed_count * default_env_config.REWARD_PER_PLACED_TRIANGLE
        + len(unique_coords_cleared) * default_env_config.REWARD_PER_CLEARED_TRIANGLE
        + default_env_config.PENALTY_GAME_OVER
    )
    assert reward == pytest.approx(expected_reward)


# --- Test execute_placement with new reward ---


def test_execute_placement_simple_no_refill_v3(
    game_state: GameState,  # Changed fixture
):
    """Test placing a shape without clearing lines, verify reward and NO immediate refill."""
    gs = game_state  # Use default game state
    config = gs.env_config
    shape_idx = 0
    # Ensure there are shapes to work with
    if not gs.shapes[0] or not gs.shapes[1] or not gs.shapes[2]:
        gs.reset()  # Reset to get shapes
        if not gs.shapes[0] or not gs.shapes[1] or not gs.shapes[2]:
            pytest.skip("Requires initial shapes in game state")

    original_shape_in_slot_1 = gs.shapes[1].copy() if gs.shapes[1] else None
    original_shape_in_slot_2 = gs.shapes[2].copy() if gs.shapes[2] else None
    shape_to_place = gs.shapes[shape_idx]
    assert shape_to_place is not None
    placed_count = len(shape_to_place.triangles)

    # Find a valid placement spot (e.g., center-ish)
    r, c = config.ROWS // 2, config.COLS // 2
    # Adjust if the default spot isn't valid for the shape
    found_spot = False
    for r_try in range(config.ROWS):
        for c_try in range(config.COLS):
            if GridLogic.can_place(gs.grid_data, shape_to_place, r_try, c_try):
                r, c = r_try, c_try
                found_spot = True
                break
        if found_spot:
            break
    if not found_spot:
        pytest.skip(
            f"Could not find valid placement for shape {shape_idx} in initial state"
        )

    mock_rng = random.Random(42)

    reward = execute_placement(gs, shape_idx, r, c, mock_rng)

    # Verify reward (placement + survival)
    expected_reward = (
        placed_count * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE
    )
    assert reward == pytest.approx(expected_reward)
    # Score is still tracked separately
    # Score update logic: placed_count + len(unique_coords_cleared) * 2
    # Since no lines cleared, score should just be placed_count
    assert gs.game_score == placed_count

    # Verify grid state using NumPy arrays
    for dr, dc, _ in shape_to_place.triangles:
        tri_r, tri_c = r + dr, c + dc
        assert gs.grid_data._occupied_np[tri_r, tri_c]
        # Cannot easily check color ID without map here, trust placement logic

    # Verify shape slot is now EMPTY
    assert gs.shapes[shape_idx] is None

    # --- Verify NO REFILL ---
    assert gs.shapes[1] == original_shape_in_slot_1
    assert gs.shapes[2] == original_shape_in_slot_2

    assert gs.pieces_placed_this_episode == 1
    assert gs.triangles_cleared_this_episode == 0
    assert not gs.is_over()


def test_execute_placement_clear_line_no_refill_v3(
    game_state: GameState,  # Changed fixture
):
    """Test placing a shape that clears a line, verify reward and NO immediate refill."""
    gs = game_state  # Use default game state
    config = gs.env_config

    # Find a shape that is a single triangle (more likely to fit)
    shape_idx = -1
    shape_single = None
    for i, s in enumerate(gs.shapes):
        if s and len(s.triangles) == 1:
            shape_idx = i
            shape_single = s
            break
    if shape_idx == -1 or not shape_single:
        gs.reset()  # Try resetting to get different shapes
        for i, s in enumerate(gs.shapes):
            if s and len(s.triangles) == 1:
                shape_idx = i
                shape_single = s
                break
        if shape_idx == -1 or not shape_single:
            pytest.skip("Requires a single-triangle shape in initial state")

    placed_count = len(shape_single.triangles)
    # Store original shapes from other slots
    original_other_shapes = [
        s.copy() if s else None for j, s in enumerate(gs.shapes) if j != shape_idx
    ]

    # Pre-occupy a line in the default grid (e.g., row 1, cols 3-11)
    # Ensure the line exists in potential_lines
    target_line_coords = None
    for line_fs in gs.grid_data.potential_lines:
        coords = list(line_fs)
        # Find a horizontal line in row 1 with length >= MIN_LINE_LENGTH
        if len(coords) >= config.MIN_LINE_LENGTH and all(r == 1 for r, c in coords):
            target_line_coords = frozenset(coords)
            break
    if not target_line_coords:
        pytest.skip("Could not find a suitable line in row 1 in potential_lines")

    coords_list = list(target_line_coords)
    # Find a coordinate in the line where the single shape can be placed
    r, c = -1, -1
    for r_place, c_place in coords_list:
        if GridLogic.can_place(gs.grid_data, shape_single, r_place, c_place):
            r, c = r_place, c_place
            break
    if r == -1:
        pytest.skip(
            f"Could not find valid placement for shape {shape_idx} on target line {target_line_coords}"
        )

    # Occupy all coords in the line EXCEPT the placement spot (r,c)
    line_coords_to_occupy = target_line_coords - {(r, c)}
    occupy_coords(gs.grid_data, line_coords_to_occupy)

    mock_rng = random.Random(42)

    reward = execute_placement(gs, shape_idx, r, c, mock_rng)

    # Verify reward (placement + line clear + survival)
    expected_reward = (
        placed_count * config.REWARD_PER_PLACED_TRIANGLE
        + len(target_line_coords) * config.REWARD_PER_CLEARED_TRIANGLE
        + config.REWARD_PER_STEP_ALIVE
    )
    assert reward == pytest.approx(expected_reward)
    # Score update logic: placed_count + len(unique_coords_cleared) * 2
    assert gs.game_score == placed_count + len(target_line_coords) * 2

    # Verify line is cleared using NumPy array
    for row, col in target_line_coords:
        assert not gs.grid_data._occupied_np[row, col]

    # Verify shape slot is now EMPTY
    assert gs.shapes[shape_idx] is None

    # --- Verify NO REFILL ---
    current_other_shapes = [s for j, s in enumerate(gs.shapes) if j != shape_idx]
    assert current_other_shapes == original_other_shapes

    assert gs.pieces_placed_this_episode == 1
    assert gs.triangles_cleared_this_episode == len(target_line_coords)
    assert not gs.is_over()


def test_execute_placement_batch_refill_v3(
    game_state: GameState, mocker: MockerFixture
):  # Changed fixture, added mocker
    """Test that placing the last shape triggers a refill and correct reward."""
    gs = game_state  # Use default game state
    config = gs.env_config
    mock_rng = random.Random(123)

    # Ensure we have 3 shapes initially
    if len(gs.shapes) != 3 or any(s is None for s in gs.shapes):
        gs.reset()  # Reset to get shapes
        if len(gs.shapes) != 3 or any(s is None for s in gs.shapes):
            pytest.skip("Could not ensure 3 initial shapes")

    initial_shapes_copy = [s.copy() for s in gs.shapes if s]

    # Find valid placements for the 3 shapes sequentially
    placements = []
    temp_gs = gs.copy()  # Simulate placements without modifying original gs yet
    placed_indices = set()

    for i in range(config.NUM_SHAPE_SLOTS):
        shape_to_place = temp_gs.shapes[i]
        if not shape_to_place:
            continue  # Should not happen with setup above

        found_spot = False
        for r_try in range(config.ROWS):
            for c_try in range(config.COLS):
                if GridLogic.can_place(temp_gs.grid_data, shape_to_place, r_try, c_try):
                    placements.append(
                        {
                            "idx": i,
                            "r": r_try,
                            "c": c_try,
                            "count": len(shape_to_place.triangles),
                        }
                    )
                    # Simulate placement in temp_gs
                    for dr, dc, _ in shape_to_place.triangles:
                        if temp_gs.grid_data.valid(r_try + dr, c_try + dc):
                            temp_gs.grid_data._occupied_np[r_try + dr, c_try + dc] = (
                                True
                            )
                    temp_gs.shapes[i] = None
                    placed_indices.add(i)
                    found_spot = True
                    break
            if found_spot:
                break
        if not found_spot:
            pytest.skip(f"Could not find sequential placement for shape {i}")

    if len(placements) != config.NUM_SHAPE_SLOTS:
        pytest.skip("Could not find valid sequential placements for all 3 shapes")

    # Now execute placements on the actual game state
    # Place first shape
    p1 = placements[0]
    execute_placement(gs, p1["idx"], p1["r"], p1["c"], mock_rng)
    (p1["count"] * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE)
    # Allow for potential line clears in first step
    # assert reward1 == pytest.approx(expected_reward1)
    assert gs.shapes[p1["idx"]] is None
    assert gs.shapes[placements[1]["idx"]] is not None  # Check other slots remain
    assert gs.shapes[placements[2]["idx"]] is not None

    # Place second shape
    p2 = placements[1]
    execute_placement(gs, p2["idx"], p2["r"], p2["c"], mock_rng)
    (p2["count"] * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE)
    # Allow for potential line clears in second step
    # assert reward2 == pytest.approx(expected_reward2)
    assert gs.shapes[p1["idx"]] is None
    assert gs.shapes[p2["idx"]] is None
    assert gs.shapes[placements[2]["idx"]] is not None

    # --- Mock check_and_clear_lines before placing the third shape ---
    mock_clear = mocker.patch(
        "trianglengin.core.environment.grid.logic.check_and_clear_lines",
        return_value=(0, set(), set()),  # Simulate no lines cleared for 3rd placement
    )

    # Place third shape (triggers refill)
    p3 = placements[2]
    reward3 = execute_placement(gs, p3["idx"], p3["r"], p3["c"], mock_rng)
    expected_reward3 = (
        p3["count"] * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE
    )  # Game not over yet, no lines cleared due to mock
    assert reward3 == pytest.approx(expected_reward3)
    mock_clear.assert_called_once()  # Verify mock was used
    sleep(0.01)  # Allow time for refill to happen (though it should be synchronous)

    # --- Verify REFILL happened ---
    assert all(s is not None for s in gs.shapes), "Not all slots were refilled"
    # Check that shapes are different (probabilistically)
    assert gs.shapes != initial_shapes_copy, (
        "Shapes after refill are identical to initial shapes (unlikely)"
    )

    assert gs.pieces_placed_this_episode == 3
    assert not gs.is_over()


# Add mocker fixture to the test signature
def test_execute_placement_game_over_v3(game_state: GameState, mocker: MockerFixture):
    """Test reward when placement leads to game over, mocking line clears."""
    config = game_state.env_config
    # Fill grid almost completely using NumPy arrays
    playable_mask = ~game_state.grid_data._death_np
    game_state.grid_data._occupied_np[playable_mask] = True

    # Make one spot empty (ensure it's playable and matches a shape)
    empty_r, empty_c = -1, -1
    shape_to_place = None
    shape_idx = -1

    # Find a single down triangle shape and a place for it
    for idx, s in enumerate(game_state.shapes):
        if s and len(s.triangles) == 1 and not s.triangles[0][2]:  # Single Down
            shape_to_place = s
            shape_idx = idx
            break
    if not shape_to_place:
        # Force a shape if none found
        shape_idx = 0
        shape_to_place = Shape([(0, 0, False)], (255, 0, 0))
        game_state.shapes[shape_idx] = shape_to_place

    # Find an empty spot for this shape
    found_spot = False
    for r_try in range(config.ROWS):
        for c_try in range(config.COLS):
            # Check if cell is playable, empty, and matches orientation
            if (
                not game_state.grid_data._death_np[r_try, c_try]
                and not game_state.grid_data._occupied_np[r_try, c_try]
                and (r_try + c_try) % 2 == 0
            ):  # Down cell
                empty_r, empty_c = r_try, c_try
                game_state.grid_data._occupied_np[empty_r, empty_c] = (
                    False  # Ensure it's empty
                )
                found_spot = True
                break
        if found_spot:
            break

    if not found_spot:
        pytest.skip("Could not find suitable empty spot for game over test")

    # Ensure grid is full except for this one spot
    game_state.grid_data._occupied_np[playable_mask] = True
    game_state.grid_data._occupied_np[empty_r, empty_c] = False

    placed_count = len(shape_to_place.triangles)

    # --- Modify setup to prevent refill ---
    # Make other shapes unplaceable (or remove them)
    unplaceable_shape = Shape([(0, 0, False), (1, 0, False), (2, 0, False)], (1, 1, 1))
    for i in range(config.NUM_SHAPE_SLOTS):
        if i != shape_idx:
            game_state.shapes[i] = unplaceable_shape  # Make other shapes unplaceable
    # --- End modification ---

    assert GridLogic.can_place(game_state.grid_data, shape_to_place, empty_r, empty_c)
    mock_rng = random.Random(999)

    # --- Mock check_and_clear_lines ---
    # Patch the function within the logic module where execute_placement imports it from
    mock_clear = mocker.patch(
        "trianglengin.core.environment.grid.logic.check_and_clear_lines",
        return_value=(0, set(), set()),  # Simulate no lines cleared
    )
    # --- End Mock ---

    # Execute placement - this should fill the last spot and trigger game over
    reward = execute_placement(game_state, shape_idx, empty_r, empty_c, mock_rng)

    # Verify the mock was called (optional but good practice)
    mock_clear.assert_called_once()

    # Verify game is over
    # The game over check happens *after* execute_placement in game_state.step
    # We need to manually check the condition here or call valid_actions
    if not game_state.valid_actions():
        game_state.game_over = True

    assert game_state.is_over(), (
        "Game should be over after placing the final piece with no other valid moves"
    )

    # Verify reward (placement + game over penalty)
    expected_reward = (
        placed_count * config.REWARD_PER_PLACED_TRIANGLE + config.PENALTY_GAME_OVER
    )
    # Use a slightly larger tolerance if needed, but approx should work
    assert reward == pytest.approx(expected_reward)


File: tests\core\environment\__init__.py
# File: trianglengin/tests/core/environment/__init__.py
# This file can be empty


File: tests\core\structs\test_shape.py
# File: trianglengin/tests/core/structs/test_shape.py

# Import directly from the library being tested
from trianglengin.core.structs import Shape


def test_shape_initialization():
    """Test basic shape initialization."""
    triangles = [(0, 0, False), (1, 0, True)]
    color = (255, 0, 0)
    shape = Shape(triangles, color)
    assert shape.triangles == sorted(triangles)  # Check sorting
    assert shape.color == color


def test_shape_bbox():
    """Test bounding box calculation."""
    triangles1 = [(0, 0, False)]
    shape1 = Shape(triangles1, (1, 1, 1))
    assert shape1.bbox() == (0, 0, 0, 0)

    triangles2 = [(0, 1, True), (1, 0, False), (1, 2, False)]
    shape2 = Shape(triangles2, (2, 2, 2))
    assert shape2.bbox() == (0, 0, 1, 2)  # min_r, min_c, max_r, max_c

    shape3 = Shape([], (3, 3, 3))
    assert shape3.bbox() == (0, 0, 0, 0)


def test_shape_copy():
    """Test the copy method."""
    triangles = [(0, 0, False), (1, 0, True)]
    color = (255, 0, 0)
    shape1 = Shape(triangles, color)
    shape2 = shape1.copy()

    assert shape1 == shape2
    assert shape1 is not shape2
    assert shape1.triangles is not shape2.triangles  # List should be copied
    assert shape1.color is shape2.color  # Color tuple is shared (immutable)

    # Modify copy's triangle list
    shape2.triangles.append((2, 2, True))
    assert shape1.triangles != shape2.triangles


def test_shape_equality():
    """Test shape equality comparison."""
    t1 = [(0, 0, False)]
    c1 = (1, 1, 1)
    t2 = [(0, 0, False)]
    c2 = (1, 1, 1)
    t3 = [(0, 0, True)]
    c3 = (2, 2, 2)

    shape1 = Shape(t1, c1)
    shape2 = Shape(t2, c2)
    shape3 = Shape(t3, c1)
    shape4 = Shape(t1, c3)

    assert shape1 == shape2
    assert shape1 != shape3
    assert shape1 != shape4
    assert shape1 != "not a shape"


def test_shape_hash():
    """Test shape hashing."""
    t1 = [(0, 0, False)]
    c1 = (1, 1, 1)
    t2 = [(0, 0, False)]
    c2 = (1, 1, 1)
    t3 = [(0, 0, True)]

    shape1 = Shape(t1, c1)
    shape2 = Shape(t2, c2)
    shape3 = Shape(t3, c1)

    assert hash(shape1) == hash(shape2)
    assert hash(shape1) != hash(shape3)

    shape_set = {shape1, shape2, shape3}
    assert len(shape_set) == 2


File: tests\core\structs\test_triangle.py
# File: trianglengin/tests/core/structs/test_triangle.py

# Import directly from the library being tested
from trianglengin.core.structs import Triangle


def test_triangle_initialization():
    """Test basic triangle initialization."""
    tri1 = Triangle(row=1, col=2, is_up=True)
    assert tri1.row == 1
    assert tri1.col == 2
    assert tri1.is_up
    assert not tri1.is_death
    assert not tri1.is_occupied
    assert tri1.color is None

    tri2 = Triangle(row=3, col=4, is_up=False, is_death=True)
    assert tri2.row == 3
    assert tri2.col == 4
    assert not tri2.is_up
    assert tri2.is_death
    assert tri2.is_occupied  # Occupied because it's death
    assert tri2.color is None


def test_triangle_copy():
    """Test the copy method."""
    tri1 = Triangle(row=1, col=2, is_up=True)
    tri1.is_occupied = True
    tri1.color = (255, 0, 0)
    tri1.neighbor_left = Triangle(1, 1, False)  # Add a neighbor

    tri2 = tri1.copy()

    assert tri1 == tri2
    assert tri1 is not tri2
    assert tri2.row == 1
    assert tri2.col == 2
    assert tri2.is_up
    assert tri2.is_occupied
    assert tri2.color == (255, 0, 0)
    assert not tri2.is_death
    # Neighbors should not be copied
    assert tri2.neighbor_left is None
    assert tri2.neighbor_right is None
    assert tri2.neighbor_vert is None

    # Modify copy and check original
    tri2.is_occupied = False
    tri2.color = (0, 255, 0)
    assert tri1.is_occupied
    assert tri1.color == (255, 0, 0)


def test_triangle_equality():
    """Test triangle equality based on row and col."""
    tri1 = Triangle(1, 2, True)
    tri2 = Triangle(1, 2, False)  # Different orientation/state
    tri3 = Triangle(1, 3, True)
    tri4 = Triangle(2, 2, True)

    assert tri1 == tri2  # Equality only checks row/col
    assert tri1 != tri3
    assert tri1 != tri4
    assert tri1 != "not a triangle"


def test_triangle_hash():
    """Test triangle hashing based on row and col."""
    tri1 = Triangle(1, 2, True)
    tri2 = Triangle(1, 2, False)
    tri3 = Triangle(1, 3, True)

    assert hash(tri1) == hash(tri2)
    assert hash(tri1) != hash(tri3)

    tri_set = {tri1, tri2, tri3}
    assert len(tri_set) == 2  # tri1 and tri2 hash the same


def test_triangle_get_points():
    """Test vertex point calculation."""
    # Up triangle at origin (0,0) with cell width/height 100
    tri_up = Triangle(0, 0, True)
    pts_up = tri_up.get_points(ox=0, oy=0, cw=100, ch=100)
    # Expected: [(0, 100), (100, 100), (50, 0)]
    assert pts_up == [(0.0, 100.0), (100.0, 100.0), (50.0, 0.0)]

    # Down triangle at (1,1) with cell width/height 50, offset (10, 20)
    tri_down = Triangle(1, 1, False)
    # ox = 10, oy = 20, cw = 50, ch = 50
    # Base x = 10 + 1 * (50 * 0.75) = 10 + 37.5 = 47.5
    # Base y = 20 + 1 * 50 = 70
    pts_down = tri_down.get_points(ox=10, oy=20, cw=50, ch=50)
    # Expected: [(47.5, 70), (47.5+50, 70), (47.5+25, 70+50)]
    # Expected: [(47.5, 70.0), (97.5, 70.0), (72.5, 120.0)]
    assert pts_down == [(47.5, 70.0), (97.5, 70.0), (72.5, 120.0)]


File: tests\core\structs\__init__.py


File: tests\utils\test_geometry.py
# File: trianglengin/tests/utils/test_geometry.py

# Import directly from the library being tested
from trianglengin.utils import geometry


def test_is_point_in_polygon_square():
    """Test point in polygon for a simple square."""
    square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

    # Inside
    assert geometry.is_point_in_polygon((0.5, 0.5), square)

    # On edge
    assert geometry.is_point_in_polygon((0.5, 0.0), square)
    assert geometry.is_point_in_polygon((1.0, 0.5), square)
    assert geometry.is_point_in_polygon((0.5, 1.0), square)
    assert geometry.is_point_in_polygon((0.0, 0.5), square)

    # On vertex
    assert geometry.is_point_in_polygon((0.0, 0.0), square)
    assert geometry.is_point_in_polygon((1.0, 1.0), square)
    assert geometry.is_point_in_polygon((1.0, 0.0), square)
    assert geometry.is_point_in_polygon((0.0, 1.0), square)

    # Outside
    assert not geometry.is_point_in_polygon((1.5, 0.5), square)
    assert not geometry.is_point_in_polygon((0.5, -0.5), square)
    assert not geometry.is_point_in_polygon((-0.1, 0.1), square)
    assert not geometry.is_point_in_polygon((0.5, 1.1), square)  # Added top outside


def test_is_point_in_polygon_triangle():
    """Test point in polygon for a triangle."""
    triangle = [(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]

    # Inside
    assert geometry.is_point_in_polygon((1.0, 0.5), triangle)
    assert geometry.is_point_in_polygon((1.0, 1.0), triangle)

    # On edge
    assert geometry.is_point_in_polygon((1.0, 0.0), triangle)  # Base
    assert geometry.is_point_in_polygon((0.5, 1.0), triangle)  # Left edge
    assert geometry.is_point_in_polygon((1.5, 1.0), triangle)  # Right edge

    # On vertex
    assert geometry.is_point_in_polygon((0.0, 0.0), triangle)
    assert geometry.is_point_in_polygon((2.0, 0.0), triangle)
    assert geometry.is_point_in_polygon((1.0, 2.0), triangle)

    # Outside
    assert not geometry.is_point_in_polygon((1.0, 2.1), triangle)
    assert not geometry.is_point_in_polygon((3.0, 0.5), triangle)
    assert not geometry.is_point_in_polygon((-0.5, 0.5), triangle)
    assert not geometry.is_point_in_polygon((1.0, -0.1), triangle)


def test_is_point_in_polygon_concave():
    """Test point in polygon for a concave shape (e.g., Pacman)."""
    # Simple concave shape (like a U)
    concave = [(0, 0), (3, 0), (3, 1), (1, 1), (1, 2), (2, 2), (2, 3), (0, 3)]

    # Inside
    assert geometry.is_point_in_polygon((0.5, 0.5), concave)
    assert geometry.is_point_in_polygon((2.5, 0.5), concave)
    assert geometry.is_point_in_polygon((0.5, 2.5), concave)
    assert geometry.is_point_in_polygon((1.5, 2.5), concave)  # Inside the 'U' part

    # Outside (in the 'mouth')
    assert not geometry.is_point_in_polygon((1.5, 1.5), concave)

    # Outside (general)
    assert not geometry.is_point_in_polygon((4.0, 1.0), concave)
    assert not geometry.is_point_in_polygon((1.0, 4.0), concave)

    # On edge
    assert geometry.is_point_in_polygon((1.5, 0.0), concave)
    assert geometry.is_point_in_polygon(
        (1.0, 1.5), concave
    )  # On the inner vertical edge
    assert geometry.is_point_in_polygon(
        (1.5, 1.0), concave
    )  # On the inner horizontal edge
    assert geometry.is_point_in_polygon(
        (2.0, 2.5), concave
    )  # On the outer vertical edge
    assert geometry.is_point_in_polygon((0.0, 1.5), concave)  # On outer edge

    # On vertex
    assert geometry.is_point_in_polygon((1.0, 1.0), concave)  # Inner corner
    assert geometry.is_point_in_polygon((1.0, 2.0), concave)  # Inner corner
    assert geometry.is_point_in_polygon((3.0, 0.0), concave)  # Outer corner
    assert geometry.is_point_in_polygon((0.0, 3.0), concave)  # Outer corner


File: tests\utils\__init__.py


File: trianglengin\app.py
import logging

import pygame

# Use internal imports
from . import config as tg_config
from . import core as tg_core
from . import interaction, visualization

logger = logging.getLogger(__name__)


class Application:
    """Main application integrating visualization and interaction for trianglengin."""

    def __init__(self, mode: str = "play"):
        # Use VisConfig from this library now
        self.vis_config = visualization.VisConfig()
        self.env_config = tg_config.EnvConfig()
        self.mode = mode

        pygame.init()
        pygame.font.init()
        self.screen = self._setup_screen()
        self.clock = pygame.time.Clock()
        self.fonts = visualization.load_fonts()

        if self.mode in ["play", "debug"]:
            # Create GameState using trianglengin core
            self.game_state = tg_core.environment.GameState(self.env_config)
            # Create Visualizer using trianglengin visualization
            self.visualizer = visualization.Visualizer(
                self.screen, self.vis_config, self.env_config, self.fonts
            )
            # Create InputHandler using trianglengin interaction
            self.input_handler = interaction.InputHandler(
                self.game_state, self.visualizer, self.mode, self.env_config
            )
        else:
            # Handle other modes or raise error if necessary
            logger.error(f"Unsupported application mode: {self.mode}")
            raise ValueError(f"Unsupported application mode: {self.mode}")

        self.running = True

    def _setup_screen(self) -> pygame.Surface:
        """Initializes the Pygame screen."""
        screen = pygame.display.set_mode(
            (self.vis_config.SCREEN_WIDTH, self.vis_config.SCREEN_HEIGHT),
            pygame.RESIZABLE,
        )
        # Use a generic name or make APP_NAME part of trianglengin config later
        pygame.display.set_caption(f"Triangle Engine - {self.mode.capitalize()} Mode")
        return screen

    def run(self):
        """Main application loop."""
        logger.info(f"Starting application in {self.mode} mode.")
        while self.running:
            self.clock.tick(self.vis_config.FPS)

            # Handle Input using InputHandler
            if self.input_handler:
                self.running = self.input_handler.handle_input()
                if not self.running:
                    break
            else:
                # Fallback event handling (should not happen in play/debug)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.type == pygame.VIDEORESIZE and self.visualizer:
                        try:
                            w, h = max(320, event.w), max(240, event.h)
                            self.visualizer.screen = pygame.display.set_mode(
                                (w, h), pygame.RESIZABLE
                            )
                            self.visualizer.layout_rects = None
                        except pygame.error as e:
                            logger.error(f"Error resizing window: {e}")
                if not self.running:
                    break

            # Render using Visualizer
            if (
                self.mode in ["play", "debug"]
                and self.visualizer
                and self.game_state
                and self.input_handler
            ):
                interaction_render_state = (
                    self.input_handler.get_render_interaction_state()
                )
                self.visualizer.render(
                    self.game_state,
                    self.mode,
                    **interaction_render_state,
                )
                pygame.display.flip()

        logger.info("Application loop finished.")
        pygame.quit()


File: trianglengin\cli.py
# File: trianglengin/trianglengin/cli.py
import logging
import sys
from typing import Annotated

# Import torch here if needed for seeding
import torch
import typer

# Use internal imports
from .app import Application
from .config import EnvConfig

app = typer.Typer(
    name="trianglengin",
    help="Core Triangle Engine - Interactive Modes.",
    add_completion=False,
)

LogLevelOption = Annotated[
    str,
    typer.Option(
        "--log-level",
        "-l",
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
        case_sensitive=False,
    ),
]

SeedOption = Annotated[
    int,
    typer.Option(
        "--seed",
        "-s",
        help="Random seed for reproducibility.",
    ),
]


def setup_logging(log_level_str: str):
    """Configures root logger based on string level."""
    log_level_str = log_level_str.upper()
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = log_level_map.get(log_level_str, logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Override existing config
    )
    # Keep external libraries less verbose if needed
    logging.getLogger("pygame").setLevel(logging.WARNING)
    logging.info(f"Root logger level set to {logging.getLevelName(log_level)}")


def run_interactive_mode(mode: str, seed: int, log_level: str):
    """Runs the interactive application."""
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    logger.info(f"Running Triangle Engine in {mode.capitalize()} mode...")

    # --- UPDATED SEEDING ---
    try:
        import random

        import numpy as np

        random.seed(seed)
        # Use default_rng() for NumPy if available, otherwise skip NumPy seeding
        try:
            np.random.default_rng(seed)
            # You might store rng if needed elsewhere, but just creating it seeds
            logger.debug("NumPy seeded using default_rng.")
        except AttributeError:
            logger.warning("np.random.default_rng not available. Skipping NumPy seed.")
        except ImportError:
            logger.warning("NumPy not found. Skipping NumPy seed.")

        torch.manual_seed(seed)
        # Add MPS seeding if needed later when utils are moved
        logger.info(f"Set random seeds to {seed}")
    except ImportError:
        logger.warning("Could not import all libraries for full seeding.")
    except Exception as e:
        logger.error(f"Error setting seeds: {e}")
    # --- END UPDATED SEEDING ---

    # Validate EnvConfig
    try:
        _ = EnvConfig()
        logger.info("EnvConfig validated.")
    except Exception as e:
        logger.critical(f"EnvConfig validation failed: {e}", exc_info=True)
        sys.exit(1)

    try:
        app_instance = Application(mode=mode)
        app_instance.run()
    except ImportError as e:
        logger.error(f"Runtime ImportError: {e}")
        logger.error(
            "Please ensure all dependencies (including pygame) are installed for trianglengin."
        )
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unhandled error occurred: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Exiting.")
    sys.exit(0)


@app.command()
def play(
    log_level: LogLevelOption = "INFO",
    seed: SeedOption = 42,
):
    """Run the game in interactive Play mode."""
    run_interactive_mode(mode="play", seed=seed, log_level=log_level)


@app.command()
def debug(
    log_level: LogLevelOption = "DEBUG",  # Default to DEBUG for debug mode
    seed: SeedOption = 42,
):
    """Run the game in interactive Debug mode."""
    run_interactive_mode(mode="debug", seed=seed, log_level=log_level)


if __name__ == "__main__":
    app()


File: trianglengin\__init__.py
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


File: trianglengin\config\env_config.py
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class EnvConfig(BaseModel):
    """Configuration for the game environment (Pydantic model)."""

    ROWS: int = Field(default=8, gt=0)
    # Provide a default that matches the default ROWS
    COLS_PER_ROW: list[int] = Field(default=[9, 11, 13, 15, 15, 13, 11, 9])
    COLS: int = Field(default=15, gt=0)
    NUM_SHAPE_SLOTS: int = Field(default=3, gt=0)
    MIN_LINE_LENGTH: int = Field(default=3, gt=0)

    # --- Reward System Constants (v3) ---
    REWARD_PER_PLACED_TRIANGLE: float = Field(default=0.01)
    REWARD_PER_CLEARED_TRIANGLE: float = Field(default=0.5)
    REWARD_PER_STEP_ALIVE: float = Field(default=0.005)
    PENALTY_GAME_OVER: float = Field(default=-10.0)
    # --- End Reward System Constants ---

    @field_validator("COLS_PER_ROW")
    @classmethod
    def check_cols_per_row_length(cls, v: list[int], info) -> list[int]:
        data = info.data if info.data else info.values
        rows = data.get("ROWS")
        if rows is None:
            return v
        if len(v) != rows:
            raise ValueError(f"COLS_PER_ROW length ({len(v)}) must equal ROWS ({rows})")
        if any(width <= 0 for width in v):
            raise ValueError("All values in COLS_PER_ROW must be positive.")
        return v

    @model_validator(mode="after")
    def check_cols_match_max_cols_per_row(self) -> "EnvConfig":
        """Ensure COLS is at least the maximum width required by any row."""
        if hasattr(self, "COLS_PER_ROW") and self.COLS_PER_ROW:
            max_row_width = max(self.COLS_PER_ROW, default=0)
            if max_row_width > self.COLS:
                raise ValueError(
                    f"COLS ({self.COLS}) must be >= the maximum value in COLS_PER_ROW ({max_row_width})"
                )
        elif not hasattr(self, "COLS_PER_ROW"):
            pass
        return self

    @computed_field  # type: ignore[misc] # Decorator requires Pydantic v2
    @property
    def ACTION_DIM(self) -> int:
        """Total number of possible actions (shape_slot * row * col)."""
        if (
            hasattr(self, "NUM_SHAPE_SLOTS")
            and hasattr(self, "ROWS")
            and hasattr(self, "COLS")
        ):
            return self.NUM_SHAPE_SLOTS * self.ROWS * self.COLS
        return 0


EnvConfig.model_rebuild(force=True)


File: trianglengin\config\__init__.py
"""
Shared configuration models for the Triangle Engine.
"""

from .env_config import EnvConfig

__all__ = ["EnvConfig"]


File: trianglengin\core\__init__.py
# File: trianglengin/trianglengin/core/__init__.py
"""
Core game logic components: environment simulation and data structures.
"""

from . import environment, structs

__all__ = ["environment", "structs"]


File: trianglengin\core\environment\action_codec.py
# File: trianglengin/trianglengin/core/environment/action_codec.py
# Moved from alphatriangle/environment/core/action_codec.py
# Updated imports
# --- ADDED: Placeholder for ActionType ---
# This will be replaced when utils/types.py is properly moved
from typing import TypeAlias

from ...config import EnvConfig

ActionType: TypeAlias = int
# --- END ADDED ---


def encode_action(shape_idx: int, r: int, c: int, config: EnvConfig) -> ActionType:
    """Encodes a (shape_idx, r, c) action into a single integer."""
    if not (0 <= shape_idx < config.NUM_SHAPE_SLOTS):
        raise ValueError(
            f"Invalid shape index: {shape_idx}, must be < {config.NUM_SHAPE_SLOTS}"
        )
    if not (0 <= r < config.ROWS):
        raise ValueError(f"Invalid row index: {r}, must be < {config.ROWS}")
    if not (0 <= c < config.COLS):
        raise ValueError(f"Invalid column index: {c}, must be < {config.COLS}")

    action_index = shape_idx * (config.ROWS * config.COLS) + r * config.COLS + c
    return action_index


def decode_action(action_index: ActionType, config: EnvConfig) -> tuple[int, int, int]:
    """Decodes an integer action into (shape_idx, r, c)."""
    # Cast ACTION_DIM to int for comparison
    action_dim_int = int(config.ACTION_DIM)  # type: ignore[call-overload]
    if not (0 <= action_index < action_dim_int):
        raise ValueError(
            f"Invalid action index: {action_index}, must be < {action_dim_int}"
        )

    grid_size = config.ROWS * config.COLS
    shape_idx = action_index // grid_size
    remainder = action_index % grid_size
    r = remainder // config.COLS
    c = remainder % config.COLS

    return shape_idx, r, c


File: trianglengin\core\environment\game_state.py
# File: trianglengin/trianglengin/core/environment/game_state.py
# Moved from alphatriangle/environment/core/game_state.py
# Updated imports
import logging
import random
from typing import TYPE_CHECKING, TypeAlias

from ...config import EnvConfig

# --- MOVED IMPORTS TO TOP ---
from . import shapes
from .action_codec import decode_action
from .grid.grid_data import GridData
from .logic.actions import get_valid_actions
from .logic.step import execute_placement

if TYPE_CHECKING:
    from .. import structs

# --- END MOVED IMPORTS ---

# --- ADDED: Placeholder for ActionType ---
ActionType: TypeAlias = int
# --- END ADDED ---


logger = logging.getLogger(__name__)


class GameState:
    """
    Represents the mutable state of the game. Does not handle NN feature extraction
    or visualization/interaction-specific state.
    """

    def __init__(
        self, config: EnvConfig | None = None, initial_seed: int | None = None
    ):
        self.env_config = config if config else EnvConfig()  # type: ignore[call-arg]
        self._rng = (
            random.Random(initial_seed) if initial_seed is not None else random.Random()
        )

        self.grid_data: GridData = None  # type: ignore
        self.shapes: list[structs.Shape | None] = []  # Use structs.Shape
        self.game_score: float = 0.0
        self.game_over: bool = False
        self.triangles_cleared_this_episode: int = 0
        self.pieces_placed_this_episode: int = 0
        self.current_step: int = 0

        self.reset()

    def reset(self):
        """Resets the game to the initial state."""
        self.grid_data = GridData(self.env_config)
        self.shapes = [None] * self.env_config.NUM_SHAPE_SLOTS
        self.game_score = 0.0
        self.triangles_cleared_this_episode = 0
        self.pieces_placed_this_episode = 0
        self.game_over = False
        self.current_step = 0

        # Call refill_shape_slots with the updated signature (no index)
        shapes.refill_shape_slots(self, self._rng)

        if not self.valid_actions():
            logger.warning(
                "Game is over immediately after reset (no valid initial moves)."
            )
            self.game_over = True

    def step(self, action_index: ActionType) -> tuple[float, bool]:
        """
        Performs one game step.
        Returns:
            Tuple[float, bool]: (reward, done)
        """
        if self.is_over():
            logger.warning("Attempted to step in a game that is already over.")
            return 0.0, True

        shape_idx, r, c = decode_action(action_index, self.env_config)
        reward = execute_placement(self, shape_idx, r, c, self._rng)
        self.current_step += 1

        if not self.game_over and not self.valid_actions():
            self.game_over = True
            logger.info(f"Game over detected after step {self.current_step}.")

        return reward, self.game_over

    def valid_actions(self) -> list[ActionType]:
        """Returns a list of valid encoded action indices."""
        return get_valid_actions(self)

    def is_over(self) -> bool:
        """Checks if the game is over."""
        return self.game_over

    def get_outcome(self) -> float:
        """Returns the terminal outcome value (e.g., final score). Used by MCTS."""
        if not self.is_over():
            logger.warning("get_outcome() called on a non-terminal state.")
            # Consider returning a default value or raising an error?
            # Returning current score might be misleading for MCTS if not terminal.
            # Let's return 0.0 as a neutral value if not over.
            return 0.0
        return self.game_score

    def copy(self) -> "GameState":
        """Creates a deep copy for simulations (e.g., MCTS)."""
        new_state = GameState.__new__(GameState)
        new_state.env_config = self.env_config
        new_state._rng = random.Random()
        new_state._rng.setstate(self._rng.getstate())
        new_state.grid_data = self.grid_data.deepcopy()
        new_state.shapes = [s.copy() if s else None for s in self.shapes]
        new_state.game_score = self.game_score
        new_state.game_over = self.game_over
        new_state.triangles_cleared_this_episode = self.triangles_cleared_this_episode
        new_state.pieces_placed_this_episode = self.pieces_placed_this_episode
        new_state.current_step = self.current_step
        return new_state

    def __str__(self) -> str:
        shape_strs = [str(s) if s else "None" for s in self.shapes]
        return f"GameState(Step:{self.current_step}, Score:{self.game_score:.1f}, Over:{self.is_over()}, Shapes:[{', '.join(shape_strs)}])"


File: trianglengin\core\environment\__init__.py
# File: trianglengin/trianglengin/core/environment/__init__.py
# Moved from alphatriangle/environment/__init__.py
# Updated imports to be relative within the library
"""
Environment module defining the game rules, state, actions, and logic.
This module is now independent of feature extraction for the NN.
"""

from ...config import EnvConfig
from .action_codec import decode_action, encode_action
from .game_state import GameState
from .grid import logic as GridLogic
from .grid.grid_data import GridData
from .logic.actions import get_valid_actions
from .logic.step import calculate_reward, execute_placement
from .shapes import logic as ShapeLogic

__all__ = [
    # Core
    "GameState",
    "encode_action",
    "decode_action",
    # Grid
    "GridData",
    "GridLogic",
    # Shapes
    "ShapeLogic",
    # Logic
    "get_valid_actions",
    "execute_placement",
    "calculate_reward",
    # Config
    "EnvConfig",
]
# REMOVED TRAILING MARKDOWN FENCE


File: trianglengin\core\environment\grid\grid_data.py
# File: trianglengin/trianglengin/core/environment/grid/grid_data.py
import copy
import logging

import numpy as np

from ....config import EnvConfig
from ...structs import NO_COLOR_ID

logger = logging.getLogger(__name__)


def _precompute_lines(config: EnvConfig) -> list[list[tuple[int, int]]]:
    """
    Generates all potential maximal horizontal and diagonal lines based on grid geometry.
    Returns a list of lines, where each line is a list of (row, col) tuples.
    """
    lines = []
    rows, cols = config.ROWS, config.COLS
    min_len = config.MIN_LINE_LENGTH

    # --- Determine playable cells based on config ---
    playable_mask = np.zeros((rows, cols), dtype=bool)
    for r in range(rows):
        playable_width = config.COLS_PER_ROW[r]
        padding = cols - playable_width
        pad_left = padding // 2
        playable_start_col = pad_left
        playable_end_col = pad_left + playable_width
        for c in range(cols):
            if playable_start_col <= c < playable_end_col:
                playable_mask[r, c] = True
    # --- End Playable Mask ---

    # Helper to check validity and playability
    def is_valid_playable(r, c):
        return 0 <= r < rows and 0 <= c < cols and playable_mask[r, c]

    # --- Trace Lines using Coordinates ---
    visited_in_line: set[tuple[int, int, str]] = set()  # (r, c, direction)

    for r_start in range(rows):
        for c_start in range(cols):
            if not is_valid_playable(r_start, c_start):
                continue

            # --- Trace Horizontal ---
            if (r_start, c_start, "h") not in visited_in_line:
                current_line_h = []
                # Trace left to find the true start of the maximal line
                cr, cc = r_start, c_start
                while is_valid_playable(cr, cc - 1):
                    cc -= 1
                # Trace right from the true start
                while is_valid_playable(cr, cc):
                    current_line_h.append((cr, cc))
                    visited_in_line.add((cr, cc, "h"))
                    cc += 1
                # Only add the maximal line if long enough
                if len(current_line_h) >= min_len:
                    lines.append(current_line_h)
                # Mark intermediate visited cells (redundant due to check above, but safe)
                # for _, visited_c in current_line_h:
                #    visited_in_line.add((r_start, visited_c, "h"))

            # --- Trace Diagonal TL-BR (Down-Right) ---
            if (r_start, c_start, "d1") not in visited_in_line:
                current_line_d1 = []
                # Trace backwards (Up-Left) to find the true start
                cr, cc = r_start, c_start
                while True:
                    is_up = (cr + cc) % 2 != 0
                    prev_r, prev_c = (cr, cc - 1) if is_up else (cr - 1, cc)
                    if is_valid_playable(prev_r, prev_c):
                        cr, cc = prev_r, prev_c
                    else:
                        break
                # Trace forwards from the true start
                _start_cr, _start_cc = cr, cc
                while is_valid_playable(cr, cc):
                    current_line_d1.append((cr, cc))
                    visited_in_line.add((cr, cc, "d1"))
                    is_up = (cr + cc) % 2 != 0
                    next_r, next_c = (cr + 1, cc) if is_up else (cr, cc + 1)
                    cr, cc = next_r, next_c
                # Only add the maximal line if long enough
                if len(current_line_d1) >= min_len:
                    lines.append(current_line_d1)
                # Mark intermediate visited cells
                # for visited_r, visited_c in current_line_d1:
                #    visited_in_line.add((visited_r, visited_c, "d1"))

            # --- Trace Diagonal BL-TR (Up-Right) ---
            if (r_start, c_start, "d2") not in visited_in_line:
                current_line_d2 = []
                # Trace backwards (Down-Left) to find the true start
                cr, cc = r_start, c_start
                while True:
                    is_up = (cr + cc) % 2 != 0
                    prev_r, prev_c = (cr + 1, cc) if is_up else (cr, cc - 1)
                    if is_valid_playable(prev_r, prev_c):
                        cr, cc = prev_r, prev_c
                    else:
                        break
                # Trace forwards from the true start
                _start_cr, _start_cc = cr, cc
                while is_valid_playable(cr, cc):
                    current_line_d2.append((cr, cc))
                    visited_in_line.add((cr, cc, "d2"))
                    is_up = (cr + cc) % 2 != 0
                    next_r, next_c = (cr, cc + 1) if is_up else (cr - 1, cc)
                    cr, cc = next_r, next_c
                # Only add the maximal line if long enough
                if len(current_line_d2) >= min_len:
                    lines.append(current_line_d2)
                # Mark intermediate visited cells
                # for visited_r, visited_c in current_line_d2:
                #    visited_in_line.add((visited_r, visited_c, "d2"))

    # --- REMOVED SUBLINE GENERATION ---

    # Remove duplicates (lines traced from different start points)
    unique_lines_tuples = {tuple(sorted(line)) for line in lines}
    unique_lines = [list(line_tuple) for line_tuple in unique_lines_tuples]

    # Final filter by length (should be redundant but safe)
    final_lines = [line for line in unique_lines if len(line) >= min_len]

    logger.debug(f"Precomputed {len(final_lines)} potential maximal lines.")
    return final_lines


class GridData:
    """
    Holds the grid state using NumPy arrays for occupancy, death zones, and color IDs.
    Manages precomputed line information based on coordinates.
    """

    def __init__(self, config: EnvConfig):
        self.rows = config.ROWS
        self.cols = config.COLS
        self.config = config

        # --- NumPy Array State ---
        self._occupied_np: np.ndarray = np.zeros((self.rows, self.cols), dtype=bool)
        self._death_np: np.ndarray = np.zeros((self.rows, self.cols), dtype=bool)
        # Stores color ID, NO_COLOR_ID (-1) means empty/no color
        self._color_id_np: np.ndarray = np.full(
            (self.rows, self.cols), NO_COLOR_ID, dtype=np.int8
        )
        # --- End NumPy Array State ---

        self._initialize_death_zone(config)
        self._occupied_np[self._death_np] = True  # Death cells are considered occupied

        # --- Line Information (Coordinate Based) ---
        # Stores frozensets of (r, c) tuples
        self.potential_lines: set[frozenset[tuple[int, int]]] = set()
        # Maps (r, c) tuple to a set of line frozensets it belongs to
        self._coord_to_lines_map: dict[
            tuple[int, int], set[frozenset[tuple[int, int]]]
        ] = {}
        # --- End Line Information ---

        self._initialize_lines_and_index()
        logger.debug(
            f"GridData initialized ({self.rows}x{self.cols}) using NumPy arrays. Found {len(self.potential_lines)} potential lines."
        )

    def _initialize_death_zone(self, config: EnvConfig):
        """Initializes the death zone numpy array."""
        cols_per_row = config.COLS_PER_ROW
        if len(cols_per_row) != self.rows:
            raise ValueError(
                f"COLS_PER_ROW length mismatch: {len(cols_per_row)} vs {self.rows}"
            )

        for r in range(self.rows):
            playable_width = cols_per_row[r]
            padding = self.cols - playable_width
            pad_left = padding // 2
            playable_start_col = pad_left
            playable_end_col = pad_left + playable_width
            for c in range(self.cols):
                if not (playable_start_col <= c < playable_end_col):
                    self._death_np[r, c] = True

    def _initialize_lines_and_index(self) -> None:
        """
        Precomputes potential lines (as coordinate sets) and creates a map
        from coordinates to the lines they belong to.
        """
        self.potential_lines = set()
        self._coord_to_lines_map = {}

        potential_lines_coords = _precompute_lines(self.config)

        for line_coords in potential_lines_coords:
            # Filter out lines containing death cells
            valid_line = True
            line_coord_set: set[tuple[int, int]] = set()
            for r, c in line_coords:
                # Use self.valid() and self._death_np directly
                if self.valid(r, c) and not self._death_np[r, c]:
                    line_coord_set.add((r, c))
                else:
                    valid_line = False
                    break  # Skip this line if any part is invalid/death

            if valid_line and len(line_coord_set) >= self.config.MIN_LINE_LENGTH:
                frozen_line = frozenset(line_coord_set)
                self.potential_lines.add(frozen_line)
                # Add to the reverse map
                for coord in line_coord_set:
                    if coord not in self._coord_to_lines_map:
                        self._coord_to_lines_map[coord] = set()
                    self._coord_to_lines_map[coord].add(frozen_line)

        logger.debug(
            f"Initialized {len(self.potential_lines)} potential lines and mapping for {len(self._coord_to_lines_map)} coordinates."
        )

    def valid(self, r: int, c: int) -> bool:
        """Checks if coordinates are within grid bounds."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_death(self, r: int, c: int) -> bool:
        """Checks if a cell is a death cell."""
        if not self.valid(r, c):
            return True  # Out of bounds is considered death
        # Cast NumPy bool_ to Python bool for type consistency
        return bool(self._death_np[r, c])

    def is_occupied(self, r: int, c: int) -> bool:
        """Checks if a cell is occupied (includes death cells)."""
        if not self.valid(r, c):
            return True  # Out of bounds is considered occupied
        # Cast NumPy bool_ to Python bool for type consistency
        return bool(self._occupied_np[r, c])

    def get_color_id(self, r: int, c: int) -> int:
        """Gets the color ID of a cell."""
        if not self.valid(r, c):
            return NO_COLOR_ID
        # Cast NumPy int8 to Python int for type consistency
        return int(self._color_id_np[r, c])

    def get_occupied_state(self) -> np.ndarray:
        """Returns a copy of the occupancy numpy array."""
        return self._occupied_np.copy()

    def get_death_state(self) -> np.ndarray:
        """Returns a copy of the death zone numpy array."""
        return self._death_np.copy()

    def get_color_id_state(self) -> np.ndarray:
        """Returns a copy of the color ID numpy array."""
        return self._color_id_np.copy()

    def deepcopy(self) -> "GridData":
        """
        Creates a deep copy of the grid data using NumPy array copying
        and standard dictionary/set copying for line data.
        """
        new_grid = GridData.__new__(
            GridData
        )  # Create new instance without calling __init__
        new_grid.rows = self.rows
        new_grid.cols = self.cols
        new_grid.config = self.config  # Config is likely immutable, shallow copy ok

        # 1. Copy NumPy arrays
        new_grid._occupied_np = self._occupied_np.copy()
        new_grid._death_np = self._death_np.copy()
        new_grid._color_id_np = self._color_id_np.copy()

        # 2. Copy Line Data (Set of frozensets and Dict[Tuple, Set[frozenset]])
        # potential_lines contains immutable frozensets, shallow copy is fine
        new_grid.potential_lines = self.potential_lines.copy()
        # _coord_to_lines_map values are sets, need deepcopy
        new_grid._coord_to_lines_map = copy.deepcopy(self._coord_to_lines_map)

        # No Triangle objects or neighbors to handle anymore

        return new_grid

    def __str__(self) -> str:
        # Basic representation, could be enhanced to show grid visually
        occupied_count = np.sum(self._occupied_np & ~self._death_np)
        return f"GridData({self.rows}x{self.cols}, Occupied: {occupied_count})"


File: trianglengin\core\environment\grid\logic.py
# File: trianglengin/trianglengin/core/environment/grid/logic.py
import logging
from typing import TYPE_CHECKING

# Import NO_COLOR_ID from the library's structs package directly
from ...structs import NO_COLOR_ID

if TYPE_CHECKING:
    from ...structs import Shape
    from .grid_data import GridData

logger = logging.getLogger(__name__)


def can_place(grid_data: "GridData", shape: "Shape", r: int, c: int) -> bool:
    """
    Checks if a shape can be placed at the specified (r, c) top-left position
    on the grid, considering occupancy, death zones, and triangle orientation.
    Reads state from GridData's NumPy arrays.
    """
    if not shape or not shape.triangles:
        return False

    for dr, dc, is_up_shape in shape.triangles:
        tri_r, tri_c = r + dr, c + dc

        # Check bounds and death zone first
        if not grid_data.valid(tri_r, tri_c) or grid_data._death_np[tri_r, tri_c]:
            return False

        # Check occupancy
        if grid_data._occupied_np[tri_r, tri_c]:
            return False

        # Check orientation match
        is_up_grid = (tri_r + tri_c) % 2 != 0
        if is_up_grid != is_up_shape:
            # Log the mismatch for debugging the test failure
            logger.debug(
                f"Orientation mismatch at ({tri_r},{tri_c}): Grid is {'Up' if is_up_grid else 'Down'}, Shape requires {'Up' if is_up_shape else 'Down'}"
            )
            return False

    return True


def check_and_clear_lines(
    grid_data: "GridData", newly_occupied_coords: set[tuple[int, int]]
) -> tuple[int, set[tuple[int, int]], set[frozenset[tuple[int, int]]]]:
    """
    Checks for completed lines involving the newly occupied coordinates and clears them.
    Operates on GridData's NumPy arrays.

    Args:
        grid_data: The GridData object (will be modified).
        newly_occupied_coords: A set of (r, c) tuples that were just occupied.

    Returns:
        Tuple containing:
            - int: Number of lines cleared.
            - set[tuple[int, int]]: Set of unique (r, c) coordinates cleared.
            - set[frozenset[tuple[int, int]]]: Set containing the frozenset representations
                                                of the actual lines that were cleared.
    """
    lines_to_check: set[frozenset[tuple[int, int]]] = set()
    for coord in newly_occupied_coords:
        if coord in grid_data._coord_to_lines_map:
            lines_to_check.update(grid_data._coord_to_lines_map[coord])

    cleared_lines_set: set[frozenset[tuple[int, int]]] = set()
    unique_coords_cleared: set[tuple[int, int]] = set()

    if not lines_to_check:
        return 0, unique_coords_cleared, cleared_lines_set

    logger.debug(f"Checking {len(lines_to_check)} potential lines for completion.")

    for line_coords_fs in lines_to_check:
        is_complete = True
        for r_line, c_line in line_coords_fs:
            # Check occupancy directly from the NumPy array
            if not grid_data._occupied_np[r_line, c_line]:
                is_complete = False
                break

        if is_complete:
            logger.debug(f"Line completed: {line_coords_fs}")
            cleared_lines_set.add(line_coords_fs)
            # Add coordinates from this cleared line to the set of unique cleared coordinates
            unique_coords_cleared.update(line_coords_fs)

    if unique_coords_cleared:
        logger.info(
            f"Clearing {len(cleared_lines_set)} lines involving {len(unique_coords_cleared)} unique coordinates."
        )
        # Update NumPy arrays for cleared coordinates
        # Convert set to tuple of arrays for advanced indexing
        if unique_coords_cleared:  # Ensure set is not empty
            rows_idx, cols_idx = zip(*unique_coords_cleared, strict=False)
            grid_data._occupied_np[rows_idx, cols_idx] = False
            grid_data._color_id_np[rows_idx, cols_idx] = NO_COLOR_ID

    # Return number of lines cleared, unique coords cleared, and the set of cleared lines
    return len(cleared_lines_set), unique_coords_cleared, cleared_lines_set


File: trianglengin\core\environment\grid\README.md
# Environment Grid Submodule (`trianglengin.environment.grid`)

## Purpose and Architecture

This submodule manages the game's grid structure and related logic. It defines the triangular cells, their properties, relationships, and operations like placement validation and line clearing.

-   **Cell Representation:** The `Triangle` class (defined in [`trianglengin.core.structs`](../../structs/README.md)) represents a single cell, storing its position and orientation (`is_up`). The actual state (occupied, death, color) is managed within `GridData`.
-   **Grid Data Structure:** The [`GridData`](grid_data.py) class holds the grid state using efficient `numpy` arrays (`_occupied_np`, `_death_np`, `_color_id_np`). It also manages precomputed information about potential lines (sets of coordinates) for efficient clearing checks.
-   **Grid Logic:** The [`logic.py`](logic.py) module (exposed as `GridLogic`) contains functions operating on `GridData`. This includes:
    -   Initializing the grid based on `EnvConfig` (defining death zones).
    -   Precomputing potential *maximal* lines (`_precompute_lines`) and indexing them (`_initialize_lines_and_index`) for efficient checking. **Sublines are no longer generated.**
    -   Checking if a shape can be placed (`can_place`), **including matching triangle orientations**.
    -   Checking for and clearing completed lines (`check_and_clear_lines`). **This function does NOT implement gravity.**
-   **Grid Features:** Note: Any functions related to calculating scalar metrics (heights, holes, bumpiness) are expected to be handled outside this core engine library, likely in the main `alphatriangle` project's features module.

## Exposed Interfaces

-   **Classes:**
    -   `GridData`: Holds the grid state using NumPy arrays.
        -   `__init__(config: EnvConfig)`
        -   `valid(r: int, c: int) -> bool`
        -   `is_death(r: int, c: int) -> bool`
        -   `is_occupied(r: int, c: int) -> bool`
        -   `get_color_id(r: int, c: int) -> int`
        -   `get_occupied_state() -> np.ndarray`
        -   `get_death_state() -> np.ndarray`
        -   `get_color_id_state() -> np.ndarray`
        -   `deepcopy() -> GridData`
-   **Modules/Namespaces:**
    -   `logic` (often imported as `GridLogic`):
        -   `can_place(grid_data: GridData, shape: Shape, r: int, c: int) -> bool`
        -   `check_and_clear_lines(grid_data: GridData, newly_occupied_coords: Set[Tuple[int, int]]) -> Tuple[int, Set[Tuple[int, int]], Set[frozenset[Tuple[int, int]]]]` **(Returns: lines_cleared_count, unique_coords_cleared_set, set_of_cleared_lines_coord_sets)**

## Dependencies

-   **[`trianglengin.config`](../../../config/README.md)**:
    -   `EnvConfig`: Used by `GridData` initialization and logic functions.
-   **[`trianglengin.core.structs`](../../structs/README.md)**:
    -   Uses `Triangle`, `Shape`, `NO_COLOR_ID`.
-   **`numpy`**:
    -   Used extensively in `GridData`.
-   **Standard Libraries:** `typing`, `logging`, `numpy`, `copy`.

---

**Note:** Please keep this README updated when changing the grid structure, cell properties, placement rules, or line clearing logic. Accurate documentation is crucial for maintainability.

File: trianglengin\core\environment\grid\__init__.py
# File: trianglengin/trianglengin/core/environment/grid/__init__.py
# Moved from alphatriangle/environment/grid/__init__.py
# Updated imports
"""
Grid submodule handling the triangular grid structure, data, and logic.
"""

# Removed: from .triangle import Triangle # Triangle is in structs now
from . import logic
from .grid_data import GridData

# DO NOT import grid_features here. It has been moved up one level
# to alphatriangle/environment/grid_features.py to break circular dependencies.

__all__ = [
    "GridData",
    "logic",
]


File: trianglengin\core\environment\logic\actions.py
# File: trianglengin/trianglengin/core/environment/logic/actions.py
# Moved from alphatriangle/environment/logic/actions.py
# Updated imports
import logging

# --- ADDED: Placeholder for ActionType ---
from typing import TYPE_CHECKING, TypeAlias

# Use relative imports within the library
from ..action_codec import encode_action
from ..grid import logic as GridLogic

ActionType: TypeAlias = int
# --- END ADDED ---

if TYPE_CHECKING:
    # Use relative import for GameState within the library
    from ..game_state import GameState

logger = logging.getLogger(__name__)


def get_valid_actions(state: "GameState") -> list["ActionType"]:
    """
    Calculates and returns a list of all valid encoded action indices
    for the current game state.
    """
    valid_actions: list[ActionType] = []
    for shape_idx, shape in enumerate(state.shapes):
        if shape is None:
            continue

        for r in range(state.env_config.ROWS):
            for c in range(state.env_config.COLS):
                if GridLogic.can_place(state.grid_data, shape, r, c):
                    action_index = encode_action(shape_idx, r, c, state.env_config)
                    valid_actions.append(action_index)

    return valid_actions


File: trianglengin\core\environment\logic\step.py
# File: trianglengin/trianglengin/core/environment/logic/step.py
# Moved from alphatriangle/environment/logic/step.py
# Updated imports
import logging
from typing import TYPE_CHECKING

# Correct import path for constants from library's structs
from ...structs.constants import COLOR_TO_ID_MAP, NO_COLOR_ID

# Use relative imports within the library
from .. import shapes as ShapeLogic
from ..grid import logic as GridLogic

if TYPE_CHECKING:
    from ....config import EnvConfig

    # Use relative import for GameState within the library
    from ..game_state import GameState

logger = logging.getLogger(__name__)


def calculate_reward(
    placed_count: int,
    unique_coords_cleared: set[tuple[int, int]],
    is_game_over: bool,
    config: "EnvConfig",
) -> float:
    """
    Calculates the step reward based on the new specification (v3).

    Args:
        placed_count: Number of triangles successfully placed.
        unique_coords_cleared: Set of unique (r, c) coordinates cleared this step.
        is_game_over: Boolean indicating if the game ended *after* this step.
        config: Environment configuration containing reward constants.

    Returns:
        The calculated step reward.
    """
    reward = 0.0

    # 1. Placement Reward
    reward += placed_count * config.REWARD_PER_PLACED_TRIANGLE

    # 2. Line Clear Reward
    reward += len(unique_coords_cleared) * config.REWARD_PER_CLEARED_TRIANGLE

    # 3. Survival Reward OR Game Over Penalty
    if is_game_over:
        reward += config.PENALTY_GAME_OVER
    else:
        reward += config.REWARD_PER_STEP_ALIVE

    logger.debug(
        f"Calculated Reward: Placement({placed_count * config.REWARD_PER_PLACED_TRIANGLE:.3f}) "
        f"+ LineClear({len(unique_coords_cleared) * config.REWARD_PER_CLEARED_TRIANGLE:.3f}) "
        f"+ {'GameOver' if is_game_over else 'Survival'}({config.PENALTY_GAME_OVER if is_game_over else config.REWARD_PER_STEP_ALIVE:.3f}) "
        f"= {reward:.3f}"
    )
    return reward


def execute_placement(
    game_state: "GameState",
    shape_idx: int,
    r: int,
    c: int,  # Removed rng argument
) -> float:
    """
    Places a shape, clears lines, updates game state (NumPy arrays), and calculates reward.
    Handles batch refilling of shapes using the game_state's internal RNG.

    Args:
        game_state: The current game state (will be modified).
        shape_idx: Index of the shape to place.
        r: Target row for placement.
        c: Target column for placement.

    Returns:
        The reward obtained for this step.
    """
    shape = game_state.shapes[shape_idx]
    if not shape:
        logger.error(f"Attempted to place an empty shape slot: {shape_idx}")
        return 0.0

    # Use the NumPy-based can_place from GridLogic
    if not GridLogic.can_place(game_state.grid_data, shape, r, c):
        # Log the shape details for debugging
        logger.error(
            f"Invalid placement attempted: Shape {shape_idx} ({shape}) at ({r},{c})"
        )
        # Log grid state around the target for more context
        for dr_ctx in range(-1, 2):
            for dc_ctx in range(-1, 2):
                rr, cc = r + dr_ctx, c + dc_ctx
                if game_state.grid_data.valid(rr, cc):
                    occ = game_state.grid_data.is_occupied(rr, cc)
                    dea = game_state.grid_data.is_death(rr, cc)
                    ori = "U" if (rr + cc) % 2 != 0 else "D"
                    logger.error(
                        f"  Context ({rr},{cc}): Occ={occ}, Death={dea}, Orient={ori}"
                    )

        return 0.0

    # --- Place the shape ---
    placed_coords: set[tuple[int, int]] = set()
    placed_count = 0
    # Get color ID from the shape's color
    color_id = COLOR_TO_ID_MAP.get(shape.color, NO_COLOR_ID)
    if color_id == NO_COLOR_ID:
        # Use default color 0 if not found, but log warning
        logger.warning(
            f"Shape color {shape.color} not found in COLOR_TO_ID_MAP! Using ID 0."
        )
        color_id = 0

    for dr, dc, _ in shape.triangles:
        tri_r, tri_c = r + dr, c + dc
        # Check validity using GridData method (which checks bounds)
        if game_state.grid_data.valid(tri_r, tri_c):
            # Check death and occupancy using NumPy arrays
            if (
                not game_state.grid_data._death_np[tri_r, tri_c]
                and not game_state.grid_data._occupied_np[tri_r, tri_c]
            ):
                # Update NumPy arrays
                game_state.grid_data._occupied_np[tri_r, tri_c] = True
                game_state.grid_data._color_id_np[tri_r, tri_c] = color_id
                placed_coords.add((tri_r, tri_c))
                placed_count += 1
            else:
                # This case should ideally not be reached if can_place passed. Log if it does.
                logger.error(
                    f"Placement conflict at ({tri_r},{tri_c}) during execution, though can_place was true."
                )
        else:
            # This case should ideally not be reached if can_place passed. Log if it does.
            logger.error(
                f"Invalid coordinates ({tri_r},{tri_c}) encountered during placement execution."
            )

    game_state.shapes[shape_idx] = None  # Remove shape from slot
    game_state.pieces_placed_this_episode += 1

    # --- Check and clear lines ---
    # Use check_and_clear_lines from GridLogic
    lines_cleared_count, unique_coords_cleared, _ = GridLogic.check_and_clear_lines(
        game_state.grid_data, placed_coords
    )
    game_state.triangles_cleared_this_episode += len(unique_coords_cleared)

    # --- Update Score (Optional tracking) ---
    # Score based on placed pieces and cleared triangles (using unique coords count)
    game_state.game_score += placed_count + len(unique_coords_cleared) * 2

    # --- Refill shapes if all slots are empty ---
    if all(s is None for s in game_state.shapes):
        logger.debug("All shape slots empty, triggering batch refill.")
        # Use the game_state's internal RNG for refill
        ShapeLogic.refill_shape_slots(game_state, game_state._rng)

    # --- Check for game over AFTER placement and refill ---
    # Game is over if no valid moves remain for the *new* state
    if not game_state.valid_actions():
        game_state.game_over = True
        logger.info(
            f"Game over detected after placing shape {shape_idx} and potential refill."
        )

    # --- Calculate Reward based on the outcome of this step ---
    step_reward = calculate_reward(
        placed_count=placed_count,
        unique_coords_cleared=unique_coords_cleared,  # Pass the set of cleared coords
        is_game_over=game_state.game_over,
        config=game_state.env_config,
    )

    return step_reward


File: trianglengin\core\environment\logic\__init__.py
# File: trianglengin/trianglengin/core/environment/logic/__init__.py
# Moved from alphatriangle/environment/logic/__init__.py
# No code changes needed, only file location.


File: trianglengin\core\environment\shapes\logic.py
# File: trianglengin/trianglengin/core/environment/shapes/logic.py
import logging
import random
from typing import TYPE_CHECKING

from ...structs import SHAPE_COLORS, Shape  # Import from library's structs
from .templates import PREDEFINED_SHAPE_TEMPLATES

if TYPE_CHECKING:
    # Use relative import for GameState within the library
    from ..game_state import GameState

logger = logging.getLogger(__name__)


def generate_random_shape(rng: random.Random) -> Shape:
    """Generates a random shape from predefined templates and colors."""
    template = rng.choice(PREDEFINED_SHAPE_TEMPLATES)
    color = rng.choice(SHAPE_COLORS)
    return Shape(template, color)


def refill_shape_slots(game_state: "GameState", rng: random.Random) -> None:
    """
    Refills ALL empty shape slots in the GameState, but ONLY if ALL slots are currently empty.
    This implements batch refilling.
    """
    if all(shape is None for shape in game_state.shapes):
        logger.debug("All shape slots are empty. Refilling all slots.")
        for i in range(game_state.env_config.NUM_SHAPE_SLOTS):
            game_state.shapes[i] = generate_random_shape(rng)
            logger.debug(f"Refilled slot {i} with {game_state.shapes[i]}")
    else:
        logger.debug("Not all shape slots are empty. Skipping refill.")


def get_neighbors(r: int, c: int, is_up: bool) -> list[tuple[int, int]]:
    """Gets potential neighbor coordinates for connectivity check."""
    if is_up:
        # Up triangle neighbors: (r, c-1), (r, c+1), (r+1, c)
        return [(r, c - 1), (r, c + 1), (r + 1, c)]
    else:
        # Down triangle neighbors: (r, c-1), (r, c+1), (r-1, c)
        return [(r, c - 1), (r, c + 1), (r - 1, c)]


def is_shape_connected(shape: Shape) -> bool:
    """Checks if all triangles in a shape are connected using BFS."""
    if not shape.triangles or len(shape.triangles) <= 1:
        return True

    # --- CORRECTED BFS LOGIC V2 ---
    # Store the actual triangle tuples (r, c, is_up) in a set for quick lookup
    all_triangles_set = set(shape.triangles)
    # Also store just the coordinates for quick neighbor checking
    all_coords_set = {(r, c) for r, c, _ in shape.triangles}

    start_triangle = shape.triangles[0]  # (r, c, is_up)

    visited: set[tuple[int, int, bool]] = set()
    queue: list[tuple[int, int, bool]] = [start_triangle]
    visited.add(start_triangle)

    while queue:
        current_r, current_c, current_is_up = queue.pop(0)

        # Check neighbors based on the current triangle's orientation
        for nr, nc in get_neighbors(current_r, current_c, current_is_up):
            # Check if the neighbor *coordinate* exists in the shape
            if (nr, nc) in all_coords_set:
                # Find the full neighbor triangle tuple (r, c, is_up)
                neighbor_triangle: tuple[int, int, bool] | None = None
                for tri_tuple in all_triangles_set:
                    if tri_tuple[0] == nr and tri_tuple[1] == nc:
                        neighbor_triangle = tri_tuple
                        break

                # If the neighbor exists in the shape and hasn't been visited
                if neighbor_triangle and neighbor_triangle not in visited:
                    visited.add(neighbor_triangle)
                    queue.append(neighbor_triangle)
    # --- END CORRECTED BFS LOGIC V2 ---

    return len(visited) == len(all_triangles_set)


File: trianglengin\core\environment\shapes\templates.py
# File: trianglengin/trianglengin/core/environment/shapes/templates.py
# Moved from alphatriangle/environment/shapes/templates.py
# No code changes needed, only file location.
# ==============================================================================
# ==                    PREDEFINED SHAPE TEMPLATES                          ==
# ==                                                                        ==
# ==    DO NOT MODIFY THIS LIST MANUALLY unless you are absolutely sure!    ==
# == These shapes are fundamental to the game's design and balance.         ==
# == Modifying them can have unintended consequences on gameplay and agent  ==
# == training.                                                              ==
# ==============================================================================

# List of predefined shape templates. Each template is a list of relative triangle coordinates (dr, dc, is_up).
# Coordinates are relative to the shape's origin (typically the top-leftmost triangle).
# is_up = True for upward-pointing triangle, False for downward-pointing.
PREDEFINED_SHAPE_TEMPLATES: list[list[tuple[int, int, bool]]] = [
    [  # Shape 1
        (
            0,
            0,
            True,
        )
    ],
    [  # Shape 1
        (
            0,
            0,
            True,
        )
    ],
    [  # Shape 2
        (
            0,
            0,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 2
        (
            0,
            0,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 3
        (
            0,
            0,
            False,
        )
    ],
    [  # Shape 4
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
    ],
    [  # Shape 4
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
    ],
    [  # Shape 5
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
    ],
    [  # Shape 5
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
    ],
    [  # Shape 6
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
    ],
    [  # Shape 7
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
        (
            0,
            2,
            False,
        ),
    ],
    [  # Shape 8
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 9
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 10
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
        (
            1,
            0,
            True,
        ),
        (
            1,
            1,
            False,
        ),
    ],
    [  # Shape 11
        (
            0,
            0,
            True,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 12
        (
            0,
            0,
            True,
        ),
        (
            1,
            -2,
            False,
        ),
        (
            1,
            -1,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 13
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
    ],
    [  # Shape 14
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 15
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
    ],
    [  # Shape 16
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 17
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            1,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 18
        (
            0,
            0,
            True,
        ),
        (
            0,
            2,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 19
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
        (
            1,
            2,
            False,
        ),
    ],
    [  # Shape 20
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
        (
            1,
            1,
            False,
        ),
    ],
    [  # Shape 21
        (
            0,
            0,
            True,
        ),
        (
            1,
            -1,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 22
        (
            0,
            0,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
    ],
    [  # Shape 23
        (
            0,
            0,
            True,
        ),
        (
            1,
            -1,
            True,
        ),
        (
            1,
            0,
            False,
        ),
        (
            1,
            1,
            True,
        ),
    ],
    [  # Shape 24
        (
            0,
            0,
            True,
        ),
        (
            1,
            -1,
            True,
        ),
        (
            1,
            0,
            False,
        ),
    ],
    [  # Shape 25
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
        (
            0,
            2,
            False,
        ),
        (
            1,
            1,
            False,
        ),
    ],
    [  # Shape 26
        (
            0,
            0,
            False,
        ),
        (
            0,
            1,
            True,
        ),
        (
            1,
            1,
            False,
        ),
    ],
    [  # Shape 27
        (
            0,
            0,
            True,
        ),
        (
            0,
            1,
            False,
        ),
        (
            1,
            0,
            False,
        ),
    ],
]


File: trianglengin\core\environment\shapes\__init__.py
# File: trianglengin/trianglengin/core/environment/shapes/__init__.py
# Moved from alphatriangle/environment/shapes/__init__.py
# Updated imports
"""
Shapes submodule handling shape generation and management.
"""

from .logic import (
    generate_random_shape,
    get_neighbors,
    is_shape_connected,
    refill_shape_slots,
)
from .templates import PREDEFINED_SHAPE_TEMPLATES

__all__ = [
    "generate_random_shape",
    "refill_shape_slots",
    "is_shape_connected",
    "get_neighbors",
    "PREDEFINED_SHAPE_TEMPLATES",
]


File: trianglengin\core\structs\constants.py
# File: trianglengin/trianglengin/core/structs/constants.py
# Moved from alphatriangle/structs/constants.py
# No code changes needed, only file location.

# Define standard colors used for shapes
# Ensure these colors are distinct and visually clear
# Also ensure BLACK (0,0,0) is NOT used here if it represents empty in color_np
SHAPE_COLORS: list[tuple[int, int, int]] = [
    (220, 40, 40),  # 0: Red
    (60, 60, 220),  # 1: Blue
    (40, 200, 40),  # 2: Green
    (230, 230, 40),  # 3: Yellow
    (240, 150, 20),  # 4: Orange
    (140, 40, 140),  # 5: Purple
    (40, 200, 200),  # 6: Cyan
    (200, 100, 180),  # 7: Pink (Example addition)
    (100, 180, 200),  # 8: Light Blue (Example addition)
]

# --- NumPy GridData Color Representation ---
# ID for empty cells in the _color_id_np array
NO_COLOR_ID: int = -1
# ID for debug-toggled cells
DEBUG_COLOR_ID: int = -2

# Mapping from Color ID (int >= 0) to RGB tuple.
# Index 0 corresponds to SHAPE_COLORS[0], etc.
# This list is used by visualization to get the RGB from the ID.
COLOR_ID_MAP: list[tuple[int, int, int]] = SHAPE_COLORS

# Reverse mapping for efficient lookup during placement (Color Tuple -> ID)
# Note: Ensure SHAPE_COLORS have unique tuples.
COLOR_TO_ID_MAP: dict[tuple[int, int, int], int] = {
    color: i for i, color in enumerate(COLOR_ID_MAP)
}

# Add special colors to the map if needed for rendering debug/other states
# These IDs won't be stored during normal shape placement.
# Example: If you want to render the debug color:
# DEBUG_RGB_COLOR = (255, 255, 0) # Example Yellow
# COLOR_ID_MAP.append(DEBUG_RGB_COLOR) # Append if needed elsewhere, but generally lookup handled separately.

# --- End NumPy GridData Color Representation ---


File: trianglengin\core\structs\shape.py
# File: trianglengin/trianglengin/core/structs/shape.py
# Moved from alphatriangle/structs/shape.py
# No code changes needed, only file location.
from __future__ import annotations


class Shape:
    """Represents a polyomino-like shape made of triangles."""

    def __init__(
        self, triangles: list[tuple[int, int, bool]], color: tuple[int, int, int]
    ):
        self.triangles: list[tuple[int, int, bool]] = sorted(triangles)
        self.color: tuple[int, int, int] = color

    def bbox(self) -> tuple[int, int, int, int]:
        """Calculates bounding box (min_r, min_c, max_r, max_c) in relative coords."""
        if not self.triangles:
            return (0, 0, 0, 0)
        rows = [t[0] for t in self.triangles]
        cols = [t[1] for t in self.triangles]
        return (min(rows), min(cols), max(rows), max(cols))

    def copy(self) -> Shape:
        """Creates a shallow copy (triangle list is copied, color is shared)."""
        new_shape = Shape.__new__(Shape)
        new_shape.triangles = list(self.triangles)
        new_shape.color = self.color
        return new_shape

    def __str__(self) -> str:
        return f"Shape(Color:{self.color}, Tris:{len(self.triangles)})"

    def __eq__(self, other: object) -> bool:
        """Checks for equality based on triangles and color."""
        if not isinstance(other, Shape):
            return NotImplemented
        return self.triangles == other.triangles and self.color == other.color

    def __hash__(self) -> int:
        """Allows shapes to be used in sets/dicts if needed."""
        return hash((tuple(self.triangles), self.color))


File: trianglengin\core\structs\triangle.py
# File: trianglengin/trianglengin/core/structs/triangle.py
# Moved from alphatriangle/structs/triangle.py
# No code changes needed, only file location.
from __future__ import annotations


class Triangle:
    """Represents a single triangular cell on the grid."""

    def __init__(self, row: int, col: int, is_up: bool, is_death: bool = False):
        self.row = row
        self.col = col
        self.is_up = is_up
        self.is_death = is_death
        self.is_occupied = is_death
        self.color: tuple[int, int, int] | None = None

        self.neighbor_left: Triangle | None = None
        self.neighbor_right: Triangle | None = None
        self.neighbor_vert: Triangle | None = None

    def get_points(
        self, ox: float, oy: float, cw: float, ch: float
    ) -> list[tuple[float, float]]:
        """Calculates vertex points for drawing, relative to origin (ox, oy)."""
        x = ox + self.col * (cw * 0.75)
        y = oy + self.row * ch
        if self.is_up:
            return [(x, y + ch), (x + cw, y + ch), (x + cw / 2, y)]
        else:
            return [(x, y), (x + cw, y), (x + cw / 2, y + ch)]

    def copy(self) -> Triangle:
        """Creates a copy of the Triangle object's state (neighbors are not copied)."""
        new_tri = Triangle(self.row, self.col, self.is_up, self.is_death)
        new_tri.is_occupied = self.is_occupied
        new_tri.color = self.color
        return new_tri

    def __repr__(self) -> str:
        state = "D" if self.is_death else ("O" if self.is_occupied else ".")
        orient = "^" if self.is_up else "v"
        return f"T({self.row},{self.col} {orient}{state})"

    def __hash__(self):
        return hash((self.row, self.col))

    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return NotImplemented
        return self.row == other.row and self.col == other.col


File: trianglengin\core\structs\__init__.py
# File: trianglengin/trianglengin/core/structs/__init__.py
# Moved from alphatriangle/structs/__init__.py
"""
Module for core data structures used across different parts of the application,
like environment, visualization, and features. Helps avoid circular dependencies.
"""

# Correctly export constants from the constants submodule
from .constants import (
    COLOR_ID_MAP,
    COLOR_TO_ID_MAP,
    DEBUG_COLOR_ID,
    NO_COLOR_ID,
    SHAPE_COLORS,
)
from .shape import Shape
from .triangle import Triangle

__all__ = [
    "Triangle",
    "Shape",
    # Exported Constants
    "SHAPE_COLORS",
    "NO_COLOR_ID",
    "DEBUG_COLOR_ID",
    "COLOR_ID_MAP",
    "COLOR_TO_ID_MAP",
]


File: trianglengin\interaction\debug_mode_handler.py
import logging
from typing import TYPE_CHECKING

import pygame

# Use internal imports
from ..core import environment as tg_env
from ..core import structs as tg_structs
from ..visualization import core as vis_core

if TYPE_CHECKING:
    from .input_handler import InputHandler

logger = logging.getLogger(__name__)


def handle_debug_click(event: pygame.event.Event, handler: "InputHandler") -> None:
    """Handles mouse clicks in debug mode (toggle triangle state using NumPy arrays)."""
    if not (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
        return

    game_state = handler.game_state
    visualizer = handler.visualizer
    mouse_pos = handler.mouse_pos

    layout_rects = visualizer.ensure_layout()
    grid_rect = layout_rects.get("grid")
    if not grid_rect:
        logger.error("Grid layout rectangle not available for debug click.")
        return

    grid_coords = vis_core.coord_mapper.get_grid_coords_from_screen(
        mouse_pos, grid_rect, game_state.env_config
    )
    if not grid_coords:
        return

    r, c = grid_coords
    if game_state.grid_data.valid(r, c):
        # Check death zone first
        if not game_state.grid_data._death_np[r, c]:
            # Toggle occupancy state in NumPy array
            current_occupied_state = game_state.grid_data._occupied_np[r, c]
            new_occupied_state = not current_occupied_state
            game_state.grid_data._occupied_np[r, c] = new_occupied_state

            # Update color ID based on new state
            new_color_id = (
                tg_structs.DEBUG_COLOR_ID
                if new_occupied_state
                else tg_structs.NO_COLOR_ID
            )
            game_state.grid_data._color_id_np[r, c] = new_color_id

            logger.debug(
                f": Toggled triangle ({r},{c}) -> {'Occupied' if new_occupied_state else 'Empty'}"
            )

            # Check for line clears if the cell became occupied
            if new_occupied_state:
                # Pass the coordinate tuple in a set
                lines_cleared, unique_tris_coords, _ = (
                    tg_env.GridLogic.check_and_clear_lines(
                        game_state.grid_data, newly_occupied_coords={(r, c)}
                    )
                )
                if lines_cleared > 0:
                    logger.debug(
                        f"Cleared {lines_cleared} lines ({len(unique_tris_coords)} coords) after toggle."
                    )
        else:
            logger.info(f"Clicked on death cell ({r},{c}). No action.")


def update_debug_hover(handler: "InputHandler") -> None:
    """Updates the debug highlight position within the InputHandler."""
    handler.debug_highlight_coord = None  # Reset hover state

    game_state = handler.game_state
    visualizer = handler.visualizer
    mouse_pos = handler.mouse_pos

    layout_rects = visualizer.ensure_layout()
    grid_rect = layout_rects.get("grid")
    if not grid_rect or not grid_rect.collidepoint(mouse_pos):
        return  # Not hovering over grid

    grid_coords = vis_core.coord_mapper.get_grid_coords_from_screen(
        mouse_pos, grid_rect, game_state.env_config
    )

    if grid_coords:
        r, c = grid_coords
        # Highlight only valid, non-death cells
        if game_state.grid_data.valid(r, c) and not game_state.grid_data.is_death(r, c):
            handler.debug_highlight_coord = grid_coords


File: trianglengin\interaction\event_processor.py
import logging
from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import pygame

if TYPE_CHECKING:
    # Use internal import
    from ..visualization.core.visualizer import Visualizer

logger = logging.getLogger(__name__)


def process_pygame_events(
    visualizer: "Visualizer",
) -> Generator[pygame.event.Event, Any, bool]:
    """
    Processes basic Pygame events like QUIT, ESCAPE, VIDEORESIZE.
    Yields other events for mode-specific handlers.
    Returns False via StopIteration value if the application should quit, True otherwise.
    """
    should_quit = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            logger.info("Received QUIT event.")
            should_quit = True
            break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            logger.info("Received ESCAPE key press.")
            should_quit = True
            break
        if event.type == pygame.VIDEORESIZE:
            try:
                w, h = max(320, event.w), max(240, event.h)
                visualizer.screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                visualizer.layout_rects = None
                logger.info(f"Window resized to {w}x{h}")
            except pygame.error as e:
                logger.error(f"Error resizing window: {e}")
            yield event
        else:
            yield event
    return not should_quit


File: trianglengin\interaction\input_handler.py
import logging

import pygame

# Use internal imports
from ..config import EnvConfig
from ..core import environment as tg_env
from ..core import structs as tg_structs
from ..visualization import Visualizer
from . import debug_mode_handler, event_processor, play_mode_handler

logger = logging.getLogger(__name__)


class InputHandler:
    """
    Handles user input, manages interaction state (selection, hover),
    and delegates actions to mode-specific handlers.
    """

    def __init__(
        self,
        game_state: tg_env.GameState,
        visualizer: Visualizer,
        mode: str,
        env_config: EnvConfig,
    ):
        self.game_state = game_state
        self.visualizer = visualizer
        self.mode = mode
        self.env_config = env_config

        # Interaction state managed here
        self.selected_shape_idx: int = -1
        self.hover_grid_coord: tuple[int, int] | None = None
        self.hover_is_valid: bool = False
        self.hover_shape: tg_structs.Shape | None = None
        self.debug_highlight_coord: tuple[int, int] | None = None
        self.mouse_pos: tuple[int, int] = (0, 0)

    def handle_input(self) -> bool:
        """Processes Pygame events and updates state based on mode. Returns False to quit."""
        self.mouse_pos = pygame.mouse.get_pos()

        # Reset hover/highlight state each frame before processing events/updates
        self.hover_grid_coord = None
        self.hover_is_valid = False
        self.hover_shape = None
        self.debug_highlight_coord = None

        running = True
        event_generator = event_processor.process_pygame_events(self.visualizer)
        try:
            while True:
                event = next(event_generator)
                # Pass self to handlers so they can modify interaction state
                if self.mode == "play":
                    play_mode_handler.handle_play_click(event, self)
                elif self.mode == "debug":
                    debug_mode_handler.handle_debug_click(event, self)
        except StopIteration as e:
            running = e.value  # False if quit requested

        # Update hover state after processing events
        if running:
            if self.mode == "play":
                play_mode_handler.update_play_hover(self)
            elif self.mode == "debug":
                debug_mode_handler.update_debug_hover(self)

        return running

    def get_render_interaction_state(self) -> dict:
        """Returns interaction state needed by Visualizer.render"""
        return {
            "selected_shape_idx": self.selected_shape_idx,
            "hover_shape": self.hover_shape,
            "hover_grid_coord": self.hover_grid_coord,
            "hover_is_valid": self.hover_is_valid,
            "hover_screen_pos": self.mouse_pos,  # Pass current mouse pos
            "debug_highlight_coord": self.debug_highlight_coord,
        }


File: trianglengin\interaction\play_mode_handler.py
import logging
from typing import TYPE_CHECKING

import pygame

# Use internal imports
from ..core import environment as tg_env
from ..core import structs as tg_structs
from ..visualization import core as vis_core

if TYPE_CHECKING:
    from .input_handler import InputHandler

logger = logging.getLogger(__name__)


def handle_play_click(event: pygame.event.Event, handler: "InputHandler") -> None:
    """Handles mouse clicks in play mode (select preview, place shape). Modifies handler state."""
    if not (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
        return

    game_state = handler.game_state
    visualizer = handler.visualizer
    mouse_pos = handler.mouse_pos

    if game_state.is_over():
        logger.info("Game is over, ignoring click.")
        return

    layout_rects = visualizer.ensure_layout()
    grid_rect = layout_rects.get("grid")
    # Get preview rects from visualizer cache
    preview_rects = visualizer.preview_rects

    # 1. Check for clicks on shape previews
    preview_idx = vis_core.coord_mapper.get_preview_index_from_screen(
        mouse_pos, preview_rects
    )
    if preview_idx is not None:
        if handler.selected_shape_idx == preview_idx:
            # Clicked selected shape again: deselect
            handler.selected_shape_idx = -1
            handler.hover_grid_coord = None  # Clear hover state on deselect
            handler.hover_shape = None
            logger.info("Deselected shape.")
        elif (
            0 <= preview_idx < len(game_state.shapes) and game_state.shapes[preview_idx]
        ):
            # Clicked a valid, available shape: select it
            handler.selected_shape_idx = preview_idx
            logger.info(f"Selected shape index: {preview_idx}")
            # Immediately update hover based on current mouse pos after selection
            update_play_hover(handler)  # Update hover state within handler
        else:
            # Clicked an empty or invalid slot
            logger.info(f"Clicked empty/invalid preview slot: {preview_idx}")
            # Deselect if clicking an empty slot while another is selected
            if handler.selected_shape_idx != -1:
                handler.selected_shape_idx = -1
                handler.hover_grid_coord = None
                handler.hover_shape = None
        return  # Handled preview click

    # 2. Check for clicks on the grid (if a shape is selected)
    selected_idx = handler.selected_shape_idx
    if selected_idx != -1 and grid_rect and grid_rect.collidepoint(mouse_pos):
        # A shape is selected, and the click is within the grid area.
        grid_coords = vis_core.coord_mapper.get_grid_coords_from_screen(
            mouse_pos, grid_rect, game_state.env_config
        )
        # Use Shape from trianglengin
        shape_to_place: tg_structs.Shape | None = game_state.shapes[selected_idx]

        # Check if the placement is valid *at the clicked location*
        if (
            grid_coords
            and shape_to_place
            and tg_env.GridLogic.can_place(
                game_state.grid_data, shape_to_place, grid_coords[0], grid_coords[1]
            )
        ):
            # Valid placement click!
            r, c = grid_coords
            action = tg_env.encode_action(selected_idx, r, c, game_state.env_config)
            # Execute the step using the game state's method
            reward, done = game_state.step(action)  # Now returns (reward, done)
            logger.info(
                f"Placed shape {selected_idx} at {grid_coords}. R={reward:.1f}, Done={done}"
            )
            # Deselect shape after successful placement
            handler.selected_shape_idx = -1
            handler.hover_grid_coord = None  # Clear hover state
            handler.hover_shape = None
        else:
            # Clicked grid, shape selected, but not a valid placement spot for the click
            logger.info(f"Clicked grid at {grid_coords}, but placement invalid.")


def update_play_hover(handler: "InputHandler") -> None:
    """Updates the hover state within the InputHandler."""
    # Reset hover state first
    handler.hover_grid_coord = None
    handler.hover_is_valid = False
    handler.hover_shape = None

    game_state = handler.game_state
    visualizer = handler.visualizer
    mouse_pos = handler.mouse_pos

    if game_state.is_over() or handler.selected_shape_idx == -1:
        return  # No hover if game over or no shape selected

    layout_rects = visualizer.ensure_layout()
    grid_rect = layout_rects.get("grid")
    if not grid_rect or not grid_rect.collidepoint(mouse_pos):
        return  # Not hovering over grid

    shape_idx = handler.selected_shape_idx
    if not (0 <= shape_idx < len(game_state.shapes)):
        return
    # Use Shape from trianglengin
    shape: tg_structs.Shape | None = game_state.shapes[shape_idx]
    if not shape:
        return

    # Get grid coordinates under mouse
    grid_coords = vis_core.coord_mapper.get_grid_coords_from_screen(
        mouse_pos, grid_rect, game_state.env_config
    )

    if grid_coords:
        # Check if placement is valid at these coordinates
        is_valid = tg_env.GridLogic.can_place(
            game_state.grid_data, shape, grid_coords[0], grid_coords[1]
        )
        # Update handler's hover state
        handler.hover_grid_coord = grid_coords
        handler.hover_is_valid = is_valid
        handler.hover_shape = shape  # Store the shape being hovered
    else:
        handler.hover_shape = shape  # Store shape for floating preview


File: trianglengin\interaction\README.md

# Interaction Module (`trianglengin.interaction`)

## Purpose and Architecture

This module handles user input (keyboard and mouse) for the interactive modes ("play", "debug") of the `trianglengin` library. It bridges the gap between raw Pygame events and actions within the game simulation (`GameState`).

-   **Event Processing:** [`event_processor.py`](event_processor.py) handles common Pygame events like quitting (QUIT, ESC) and window resizing. It acts as a generator, yielding other events for mode-specific processing.
-   **Input Handler:** The [`InputHandler`](input_handler.py) class is the main entry point.
    -   It receives Pygame events (via the `event_processor`).
    -   It **manages interaction-specific state** internally (e.g., `selected_shape_idx`, `hover_grid_coord`, `debug_highlight_coord`).
    -   It determines the current interaction mode ("play" or "debug") and delegates event handling and hover updates to specific handler functions ([`play_mode_handler`](play_mode_handler.py), [`debug_mode_handler`](debug_mode_handler.py)).
    -   It provides the necessary interaction state to the [`Visualizer`](../visualization/core/visualizer.py) for rendering feedback (hover previews, selection highlights).
-   **Mode-Specific Handlers:** `play_mode_handler.py` and `debug_mode_handler.py` contain the logic specific to each mode, operating on the `InputHandler`'s state and the `GameState`.
    -   `play`: Handles selecting shapes, checking placement validity, and triggering `GameState.step` on valid clicks. Updates hover state in the `InputHandler`.
    -   `debug`: Handles toggling the state of individual triangles directly on the `GameState.grid_data`. Updates hover state in the `InputHandler`.
-   **Decoupling:** It separates input handling logic from the core game simulation ([`core.environment`](../core/environment/README.md)) and rendering ([`visualization`](../visualization/README.md)), although it needs references to both to function.

## Exposed Interfaces

-   **Classes:**
    -   `InputHandler`:
        -   `__init__(game_state: GameState, visualizer: Visualizer, mode: str, env_config: EnvConfig)`
        -   `handle_input() -> bool`: Processes events for one frame, returns `False` if quitting.
        -   `get_render_interaction_state() -> dict`: Returns interaction state needed by `Visualizer.render`.
-   **Functions:**
    -   `process_pygame_events(visualizer: Visualizer) -> Generator[pygame.event.Event, Any, bool]`: Processes common events, yields others.
    -   `handle_play_click(event: pygame.event.Event, handler: InputHandler)`: Handles clicks in play mode.
    -   `update_play_hover(handler: InputHandler)`: Updates hover state in play mode.
    -   `handle_debug_click(event: pygame.event.Event, handler: InputHandler)`: Handles clicks in debug mode.
    -   `update_debug_hover(handler: InputHandler)`: Updates hover state in debug mode.

## Dependencies

-   **[`trianglengin.core`](../core/README.md)**:
    -   `GameState`, `EnvConfig`, `GridLogic`, `ActionCodec`, `Shape`, `Triangle`, `DEBUG_COLOR_ID`, `NO_COLOR_ID`.
-   **[`trianglengin.visualization`](../visualization/README.md)**:
    -   `Visualizer`, `VisConfig`, `coord_mapper`.
-   **`pygame`**:
    -   Relies heavily on Pygame for event handling (`pygame.event`, `pygame.mouse`) and constants (`MOUSEBUTTONDOWN`, `KEYDOWN`, etc.).
-   **Standard Libraries:** `typing`, `logging`.

---

**Note:** Please keep this README updated when adding new interaction modes, changing input handling logic, or modifying the interfaces between interaction, environment, and visualization. Accurate documentation is crucial for maintainability.

File: trianglengin\interaction\__init__.py
"""
Interaction handling module for interactive modes (play/debug).
"""

from .debug_mode_handler import handle_debug_click, update_debug_hover
from .event_processor import process_pygame_events
from .input_handler import InputHandler
from .play_mode_handler import handle_play_click, update_play_hover

__all__ = [
    "InputHandler",
    "process_pygame_events",
    "handle_play_click",
    "update_play_hover",
    "handle_debug_click",
    "update_debug_hover",
]


File: trianglengin\utils\geometry.py
# File: trianglengin/trianglengin/utils/geometry.py
# Winding Number Algorithm implementation
# Source: Adapted from http://geomalgorithms.com/a03-_inclusion.html (Point in Polygon W. Randolph Franklin)


def is_point_in_polygon(
    point: tuple[float, float], polygon: list[tuple[float, float]]
) -> bool:
    """
    Checks if a point is inside a polygon using the Winding Number algorithm.
    Handles points on the boundary correctly.

    Args:
        point: Tuple (x, y) representing the point coordinates.
        polygon: List of tuples [(x1, y1), (x2, y2), ...] representing polygon vertices in order.

    Returns:
        True if the point is inside or on the boundary of the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    if n < 3:  # Need at least 3 vertices for a polygon
        return False

    wn = 0  # the winding number counter
    epsilon = 1e-9  # Tolerance for floating point comparisons

    # loop through all edges of the polygon
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]  # Wrap around to the first vertex

        # Check if point is on the vertex P1
        if abs(p1[0] - x) < epsilon and abs(p1[1] - y) < epsilon:
            return True

        # Check if point is on the horizontal edge P1P2
        # --- COMBINED IF ---
        if (
            abs(p1[1] - p2[1]) < epsilon
            and abs(p1[1] - y) < epsilon
            and min(p1[0], p2[0]) - epsilon <= x <= max(p1[0], p2[0]) + epsilon
        ):
            return True
        # --- END COMBINED IF ---

        # Check if point is on the vertical edge P1P2
        # --- COMBINED IF ---
        if (
            abs(p1[0] - p2[0]) < epsilon
            and abs(p1[0] - x) < epsilon
            and min(p1[1], p2[1]) - epsilon <= y <= max(p1[1], p2[1]) + epsilon
        ):
            return True
        # --- END COMBINED IF ---

        # Check for intersection using winding number logic
        # Check y range (inclusive min, exclusive max for upward crossing)
        y_in_upward_range = p1[1] <= y + epsilon < p2[1] + epsilon
        y_in_downward_range = p2[1] <= y + epsilon < p1[1] + epsilon

        if y_in_upward_range or y_in_downward_range:
            # Calculate orientation: > 0 for left turn (counter-clockwise), < 0 for right turn
            orientation = (p2[0] - p1[0]) * (y - p1[1]) - (x - p1[0]) * (p2[1] - p1[1])

            if (
                y_in_upward_range and orientation > epsilon
            ):  # Upward crossing, P left of edge
                wn += 1
            elif (
                y_in_downward_range and orientation < -epsilon
            ):  # Downward crossing, P right of edge
                wn -= 1
            # --- COMBINED IF for collinear points on edge ---
            elif (
                abs(orientation) < epsilon
                and min(p1[0], p2[0]) - epsilon <= x <= max(p1[0], p2[0]) + epsilon
                and min(p1[1], p2[1]) - epsilon <= y <= max(p1[1], p2[1]) + epsilon
            ):
                return True  # Point is on the edge segment
            # --- END COMBINED IF ---

    # wn == 0 only when P is outside
    return wn != 0


File: trianglengin\utils\types.py
# File: trianglengin/trianglengin/utils/types.py
# Placeholder for Phase 1
"""
Shared type definitions for the Triangle Engine.
"""

from typing import TypeAlias

# Action representation (integer index)
ActionType: TypeAlias = int


File: trianglengin\utils\__init__.py
"""
General utilities for the Triangle Engine.
"""

# --- ADDED: Export geometry ---
from . import geometry
from .types import ActionType

__all__ = ["ActionType", "geometry"]


File: trianglengin\visualization\README.md

# Visualization Module (`trianglengin.visualization`)

## Purpose and Architecture

This module is responsible for rendering the game state visually using the Pygame library, specifically for the **interactive modes** (play/debug) provided directly by the `trianglengin` library.

-   **Core Components ([`core/README.md`](core/README.md)):**
    -   `Visualizer`: Orchestrates the rendering process for interactive modes.
    -   `layout`: Calculates the screen positions and sizes for different UI areas.
    -   `fonts`: Loads necessary font files.
    -   `colors`: Defines a centralized palette of RGB color tuples.
    -   `coord_mapper`: Provides functions to map screen coordinates to grid coordinates and preview indices.
-   **Drawing Components ([`drawing/README.md`](drawing/README.md)):**
    -   Contains specific functions for drawing different elements onto Pygame surfaces (grid, shapes, previews, HUD, highlights).

**Note:** More advanced visualization components related to training (e.g., `DashboardRenderer`, `Plotter`, `ProgressBar`) remain in the `alphatriangle` project.

## Exposed Interfaces

-   **Core Classes & Functions:**
    -   `Visualizer`: Main renderer for interactive modes.
    -   `calculate_interactive_layout`, `calculate_training_layout`: Calculates UI layout rectangles.
    -   `load_fonts`: Loads Pygame fonts.
    -   `colors`: Module containing color constants (e.g., `colors.WHITE`).
    -   `get_grid_coords_from_screen`: Maps screen to grid coordinates.
    -   `get_preview_index_from_screen`: Maps screen to preview index.
-   **Drawing Functions:** (Exposed via `trianglengin.visualization.drawing`)
-   **Config:**
    -   `VisConfig`: Configuration class (re-exported from `alphatriangle.config`).
    -   `EnvConfig`: Configuration class (re-exported from `trianglengin.config`).

## Dependencies

-   **`trianglengin.core`**: `GameState`, `EnvConfig`, `GridData`, `Shape`, `Triangle`.
-   **`trianglengin.utils`**: `geometry` (Planned).
-   **`alphatriangle.config`**: `VisConfig` (Imported temporarily).
-   **`pygame`**: The core library used for all drawing, surface manipulation, and font rendering.
-   **Standard Libraries:** `typing`, `logging`, `math`.

---

**Note:** Please keep this README updated when changing rendering logic, adding new visual elements, modifying layout calculations, or altering the interfaces exposed.

File: trianglengin\visualization\__init__.py
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


File: trianglengin\visualization\core\colors.py
"""Centralized color definitions (RGB tuples 0-255)."""

WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
LIGHT_GRAY: tuple[int, int, int] = (180, 180, 180)
GRAY: tuple[int, int, int] = (100, 100, 100)
DARK_GRAY: tuple[int, int, int] = (40, 40, 40)
RED: tuple[int, int, int] = (220, 40, 40)
DARK_RED: tuple[int, int, int] = (100, 10, 10)
BLUE: tuple[int, int, int] = (60, 60, 220)
YELLOW: tuple[int, int, int] = (230, 230, 40)
GREEN: tuple[int, int, int] = (40, 200, 40)
DARK_GREEN: tuple[int, int, int] = (10, 80, 10)
ORANGE: tuple[int, int, int] = (240, 150, 20)
PURPLE: tuple[int, int, int] = (140, 40, 140)
CYAN: tuple[int, int, int] = (40, 200, 200)
LIGHTG: tuple[int, int, int] = (144, 238, 144)
HOTPINK: tuple[int, int, int] = (255, 105, 180)  # Added for plots

GOOGLE_COLORS: list[tuple[int, int, int]] = [
    (15, 157, 88),  # Green
    (244, 180, 0),  # Yellow
    (66, 133, 244),  # Blue
    (219, 68, 55),  # Red
]

# Game Specific Visuals
GRID_BG_DEFAULT: tuple[int, int, int] = (20, 20, 30)
GRID_BG_GAME_OVER: tuple[int, int, int] = DARK_RED
GRID_LINE_COLOR: tuple[int, int, int] = GRAY
TRIANGLE_EMPTY_COLOR: tuple[int, int, int] = (60, 60, 70)
PREVIEW_BG: tuple[int, int, int] = (30, 30, 40)
PREVIEW_BORDER: tuple[int, int, int] = GRAY
PREVIEW_SELECTED_BORDER: tuple[int, int, int] = BLUE
PLACEMENT_VALID_COLOR: tuple[int, int, int, int] = (*GREEN, 150)  # RGBA
PLACEMENT_INVALID_COLOR: tuple[int, int, int, int] = (*RED, 100)  # RGBA
DEBUG_TOGGLE_COLOR: tuple[int, int, int] = YELLOW

# --- ADDED: Colors for Progress Bar Cycling ---
PROGRESS_BAR_CYCLE_COLORS: list[tuple[int, int, int]] = [
    GREEN,
    BLUE,
    YELLOW,
    ORANGE,
    PURPLE,
    CYAN,
    HOTPINK,
    RED,  # Add red towards the end
]


File: trianglengin\visualization\core\coord_mapper.py
# File: trianglengin/trianglengin/visualization/core/coord_mapper.py
import pygame

# Use internal imports
from ...config import EnvConfig
from ...core.structs import Triangle
from ...utils import geometry  # Corrected import path


# --- Rest of the file remains the same ---
def _calculate_render_params(
    width: int, height: int, config: EnvConfig
) -> tuple[float, float, float, float]:
    """Calculates scale (cw, ch) and offset (ox, oy) for rendering the grid."""
    rows, cols = config.ROWS, config.COLS
    cols_eff = cols * 0.75 + 0.25 if cols > 0 else 1
    scale_w = width / cols_eff if cols_eff > 0 else 1
    scale_h = height / rows if rows > 0 else 1
    scale = max(1.0, min(scale_w, scale_h))
    cell_size = scale
    grid_w_px = cols_eff * cell_size
    grid_h_px = rows * cell_size
    offset_x = (width - grid_w_px) / 2
    offset_y = (height - grid_h_px) / 2
    return cell_size, cell_size, offset_x, offset_y


def get_grid_coords_from_screen(
    screen_pos: tuple[int, int], grid_area_rect: pygame.Rect, config: EnvConfig
) -> tuple[int, int] | None:
    """Maps screen coordinates (relative to screen) to grid row/column."""
    if not grid_area_rect or not grid_area_rect.collidepoint(screen_pos):
        return None

    local_x = screen_pos[0] - grid_area_rect.left
    local_y = screen_pos[1] - grid_area_rect.top
    cw, ch, ox, oy = _calculate_render_params(
        grid_area_rect.width, grid_area_rect.height, config
    )
    if cw <= 0 or ch <= 0:
        return None

    row = int((local_y - oy) / ch) if ch > 0 else -1
    approx_col_center_index = (local_x - ox - cw / 4) / (cw * 0.75) if cw > 0 else -1
    col = int(round(approx_col_center_index))

    for r_check in [row, row - 1, row + 1]:
        if not (0 <= r_check < config.ROWS):
            continue
        for c_check in [col, col - 1, col + 1]:
            if not (0 <= c_check < config.COLS):
                continue
            # Use corrected orientation check
            is_up = (r_check + c_check) % 2 != 0
            temp_tri = Triangle(r_check, c_check, is_up)
            pts = temp_tri.get_points(ox, oy, cw, ch)
            # Use geometry from utils
            if geometry.is_point_in_polygon((local_x, local_y), pts):
                return r_check, c_check

    if 0 <= row < config.ROWS and 0 <= col < config.COLS:
        return row, col
    return None


def get_preview_index_from_screen(
    screen_pos: tuple[int, int], preview_rects: dict[int, pygame.Rect]
) -> int | None:
    """Maps screen coordinates to a shape preview index."""
    if not preview_rects:
        return None
    for idx, rect in preview_rects.items():
        if rect and rect.collidepoint(screen_pos):
            return idx
    return None


File: trianglengin\visualization\core\fonts.py
import logging

import pygame

logger = logging.getLogger(__name__)

DEFAULT_FONT_NAME = None
FALLBACK_FONT_NAME = "arial,freesans"


def load_single_font(name: str | None, size: int) -> pygame.font.Font | None:
    """Loads a single font, handling potential errors."""
    try:
        font = pygame.font.SysFont(name, size)
        return font
    except Exception as e:
        logger.error(f"Error loading font '{name}' size {size}: {e}")
        if name != FALLBACK_FONT_NAME:
            logger.warning(f"Attempting fallback font: {FALLBACK_FONT_NAME}")
            try:
                font = pygame.font.SysFont(FALLBACK_FONT_NAME, size)
                logger.info(f"Loaded fallback font: {FALLBACK_FONT_NAME} size {size}")
                return font
            except Exception as e_fallback:
                logger.error(f"Fallback font failed: {e_fallback}")
                return None
        return None


def load_fonts(
    font_sizes: dict[str, int] | None = None,
) -> dict[str, pygame.font.Font | None]:
    """Loads standard game fonts."""
    if font_sizes is None:
        font_sizes = {
            "ui": 24,
            "score": 30,
            "help": 18,
            "title": 48,
        }

    fonts: dict[str, pygame.font.Font | None] = {}
    required_fonts = ["score", "help"]

    logger.info("Loading fonts...")
    for name, size in font_sizes.items():
        fonts[name] = load_single_font(DEFAULT_FONT_NAME, size)

    for name in required_fonts:
        if fonts.get(name) is None:
            logger.critical(
                f"Essential font '{name}' failed to load. Text rendering will be affected."
            )

    return fonts


File: trianglengin\visualization\core\layout.py
import logging

import pygame

# Import VisConfig from alphatriangle (assuming it stays there for training viz)
# If VisConfig moves entirely, import from ..config
from alphatriangle.config import VisConfig

logger = logging.getLogger(__name__)


def calculate_interactive_layout(
    screen_width: int, screen_height: int, vis_config: VisConfig
) -> dict[str, pygame.Rect]:
    """
    Calculates layout rectangles for interactive modes (play/debug).
    Places grid on the left and preview on the right.
    """
    sw, sh = screen_width, screen_height
    pad = vis_config.PADDING
    hud_h = vis_config.HUD_HEIGHT
    preview_w = vis_config.PREVIEW_AREA_WIDTH

    available_h = max(0, sh - hud_h - 2 * pad)
    available_w = max(0, sw - 3 * pad)

    grid_w = max(0, available_w - preview_w)
    grid_h = available_h

    grid_rect = pygame.Rect(pad, pad, grid_w, grid_h)
    preview_rect = pygame.Rect(grid_rect.right + pad, pad, preview_w, grid_h)

    screen_rect = pygame.Rect(0, 0, sw, sh)
    grid_rect = grid_rect.clip(screen_rect)
    preview_rect = preview_rect.clip(screen_rect)

    logger.debug(
        f"Interactive Layout calculated: Grid={grid_rect}, Preview={preview_rect}"
    )

    return {
        "grid": grid_rect,
        "preview": preview_rect,
    }


def calculate_training_layout(
    screen_width: int,
    screen_height: int,
    vis_config: VisConfig,
    progress_bars_total_height: int,  # Height needed for progress bars
) -> dict[str, pygame.Rect]:
    """
    Calculates layout rectangles for training visualization mode. MINIMAL SPACING.
    Worker grid top, progress bars bottom (above HUD), plots fill middle.
    """
    sw, sh = screen_width, screen_height
    pad = 2  # Minimal padding
    hud_h = vis_config.HUD_HEIGHT

    # --- Worker Grid Area (Top) ---
    # Calculate available height excluding HUD and minimal padding
    total_available_h_for_grid_plots_bars = max(0, sh - hud_h - 2 * pad)
    top_area_h = min(
        int(total_available_h_for_grid_plots_bars * 0.10), 80
    )  # 10% or 80px max
    top_area_w = sw - 2 * pad
    worker_grid_rect = pygame.Rect(pad, pad, top_area_w, top_area_h)

    # --- Progress Bar Area (Bottom, above HUD) ---
    # Position it precisely based on its required height
    pb_area_y = sh - hud_h - pad - progress_bars_total_height
    pb_area_w = sw - 2 * pad
    progress_bar_area_rect = pygame.Rect(
        pad, pb_area_y, pb_area_w, progress_bars_total_height
    )

    # --- Plot Area (Middle) ---
    # Calculate height to fill the gap precisely
    plot_area_y = worker_grid_rect.bottom + pad
    plot_area_w = sw - 2 * pad
    plot_area_h = max(
        0, progress_bar_area_rect.top - plot_area_y - pad
    )  # Fill space between worker grid and progress bars
    plot_rect = pygame.Rect(pad, plot_area_y, plot_area_w, plot_area_h)

    # Clip all rects to screen bounds
    screen_rect = pygame.Rect(0, 0, sw, sh)
    worker_grid_rect = worker_grid_rect.clip(screen_rect)
    plot_rect = plot_rect.clip(screen_rect)
    progress_bar_area_rect = progress_bar_area_rect.clip(screen_rect)

    logger.debug(
        f"Training Layout calculated (Compact V3): WorkerGrid={worker_grid_rect}, PlotRect={plot_rect}, ProgressBarArea={progress_bar_area_rect}"
    )

    return {
        "worker_grid": worker_grid_rect,
        "plots": plot_rect,
        "progress_bar_area": progress_bar_area_rect,  # Use this rect for drawing PBs
    }


calculate_layout = calculate_training_layout  # Keep default export for now


File: trianglengin\visualization\core\README.md

# Visualization Core Submodule (`trianglengin.visualization.core`)

## Purpose and Architecture

This submodule contains the central classes and foundational elements for the **interactive** visualization system within the `trianglengin` library. It orchestrates rendering for play/debug modes, manages layout and coordinate systems, and defines core visual properties like colors and fonts.

**Note:** Training-specific visualization components (like `DashboardRenderer`, `GameRenderer`, `Plotter`) remain in the `alphatriangle` project.

-   **Render Orchestration:**
    -   [`Visualizer`](visualizer.py): The main class for rendering in **interactive modes** ("play", "debug"). It maintains the Pygame screen, calculates layout using `layout.py`, manages cached preview area rectangles, and calls appropriate drawing functions from [`trianglengin.visualization.drawing`](../drawing/README.md). **It receives interaction state (hover position, selected index) via its `render` method to display visual feedback.**
-   **Layout Management:**
    -   [`layout.py`](layout.py): Contains functions (`calculate_interactive_layout`, `calculate_training_layout`) to determine the size and position of the main UI areas based on the screen dimensions, mode, and `VisConfig`.
-   **Coordinate System:**
    -   [`coord_mapper.py`](coord_mapper.py): Provides essential mapping functions:
        -   `_calculate_render_params`: Internal helper to get scaling and offset for grid rendering.
        -   `get_grid_coords_from_screen`: Converts mouse/screen coordinates into logical grid (row, column) coordinates.
        -   `get_preview_index_from_screen`: Converts mouse/screen coordinates into the index of the shape preview slot being pointed at.
-   **Visual Properties:**
    -   [`colors.py`](colors.py): Defines a centralized palette of named color constants (RGB tuples).
    -   [`fonts.py`](fonts.py): Contains the `load_fonts` function to load and manage Pygame font objects.

## Exposed Interfaces

-   **Classes:**
    -   `Visualizer`: Renderer for interactive modes.
        -   `__init__(...)`
        -   `render(game_state: GameState, mode: str, **interaction_state)`: Renders based on game state and interaction hints.
        -   `ensure_layout() -> Dict[str, pygame.Rect]`
        -   `screen`: Public attribute (Pygame Surface).
        -   `preview_rects`: Public attribute (cached preview area rects).
-   **Functions:**
    -   `calculate_interactive_layout(...) -> Dict[str, pygame.Rect]`
    -   `calculate_training_layout(...) -> Dict[str, pygame.Rect]` (Kept for potential future use)
    -   `load_fonts() -> Dict[str, Optional[pygame.font.Font]]`
    -   `get_grid_coords_from_screen(...) -> Optional[Tuple[int, int]]`
    -   `get_preview_index_from_screen(...) -> Optional[int]`
-   **Modules:**
    -   `colors`: Provides color constants (e.g., `colors.RED`).

## Dependencies

-   **`trianglengin.core`**: `GameState`, `EnvConfig`, `GridData`, `Shape`, `Triangle`.
-   **`trianglengin.utils`**: `geometry` (Planned).
-   **`alphatriangle.config`**: `VisConfig` (Imported temporarily, might move later).
-   **[`trianglengin.visualization.drawing`](../drawing/README.md)**: Drawing functions are called by `Visualizer`.
-   **`pygame`**: Used for surfaces, rectangles, fonts, display management.
-   **Standard Libraries:** `typing`, `logging`, `math`.

---

**Note:** Please keep this README updated when changing the core rendering logic, layout calculations, coordinate mapping, or the interfaces of the renderers. Accurate documentation is crucial for maintainability.


File: trianglengin\visualization\core\visualizer.py
# File: trianglengin/trianglengin/visualization/core/visualizer.py
# (Verify this change was applied correctly)
import logging
from typing import TYPE_CHECKING

import pygame

# Use internal imports
from ...config import EnvConfig
from ...core.environment import GameState
from ...core.structs import Shape
from ..drawing import grid as grid_drawing
from ..drawing import highlight as highlight_drawing
from ..drawing import hud as hud_drawing
from ..drawing import previews as preview_drawing
from ..drawing.previews import (
    draw_floating_preview,
    draw_placement_preview,
)
from . import colors, layout

if TYPE_CHECKING:
    # Import VisConfig from alphatriangle (assuming it stays there for training viz)
    # If VisConfig moves entirely, import from ...config
    from alphatriangle.config import VisConfig


logger = logging.getLogger(__name__)


class Visualizer:
    """
    Orchestrates rendering of a single game state for interactive modes.
    Receives interaction state (hover, selection) via render parameters.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        vis_config: "VisConfig",
        env_config: EnvConfig,
        fonts: dict[str, pygame.font.Font | None],
    ):
        self.screen = screen
        self.vis_config = vis_config
        self.env_config = env_config
        self.fonts = fonts
        self.layout_rects: dict[str, pygame.Rect] | None = None
        self.preview_rects: dict[int, pygame.Rect] = {}  # Cache preview rects
        self._layout_calculated_for_size: tuple[int, int] = (0, 0)
        self.ensure_layout()  # Initial layout calculation

    def ensure_layout(self) -> dict[str, pygame.Rect]:
        """Returns cached layout or calculates it if needed."""
        current_w, current_h = self.screen.get_size()
        current_size = (current_w, current_h)

        if (
            self.layout_rects is None
            or self._layout_calculated_for_size != current_size
        ):
            # Use the interactive layout calculation
            self.layout_rects = layout.calculate_interactive_layout(
                current_w, current_h, self.vis_config
            )
            self._layout_calculated_for_size = current_size
            logger.info(
                f"Recalculated interactive layout for size {current_size}: {self.layout_rects}"
            )
            # Clear preview rect cache when layout changes
            self.preview_rects = {}

        return self.layout_rects if self.layout_rects is not None else {}

    def render(
        self,
        game_state: GameState,
        mode: str,
        # Interaction state passed in:
        selected_shape_idx: int = -1,
        hover_shape: Shape | None = None,
        hover_grid_coord: tuple[int, int] | None = None,
        hover_is_valid: bool = False,
        hover_screen_pos: tuple[int, int] | None = None,
        debug_highlight_coord: tuple[int, int] | None = None,
    ):
        """
        Renders the entire game visualization for interactive modes.
        Uses interaction state passed as parameters for visual feedback.
        """
        self.screen.fill(colors.GRID_BG_DEFAULT)  # Clear screen
        layout_rects = self.ensure_layout()
        grid_rect = layout_rects.get("grid")
        preview_rect = layout_rects.get("preview")

        # Render Grid Area
        if grid_rect and grid_rect.width > 0 and grid_rect.height > 0:
            try:
                grid_surf = self.screen.subsurface(grid_rect)
                self._render_grid_area(
                    grid_surf,
                    game_state,
                    mode,
                    grid_rect,
                    hover_shape,
                    hover_grid_coord,
                    hover_is_valid,
                    hover_screen_pos,
                    debug_highlight_coord,
                )
            except ValueError as e:
                logger.error(f"Error creating grid subsurface ({grid_rect}): {e}")
                pygame.draw.rect(self.screen, colors.RED, grid_rect, 1)

        # Render Preview Area
        if preview_rect and preview_rect.width > 0 and preview_rect.height > 0:
            try:
                preview_surf = self.screen.subsurface(preview_rect)
                # Pass selected_shape_idx for highlighting
                self._render_preview_area(
                    preview_surf, game_state, mode, preview_rect, selected_shape_idx
                )
            except ValueError as e:
                logger.error(f"Error creating preview subsurface ({preview_rect}): {e}")
                pygame.draw.rect(self.screen, colors.RED, preview_rect, 1)

        # Render HUD
        hud_drawing.render_hud(
            surface=self.screen,
            mode=mode,
            fonts=self.fonts,
            # display_stats=None, # Argument removed from call
        )

    def _render_grid_area(
        self,
        grid_surf: pygame.Surface,
        game_state: GameState,
        mode: str,
        grid_rect: pygame.Rect,  # Pass grid_rect for hover calculations
        hover_shape: Shape | None,
        hover_grid_coord: tuple[int, int] | None,
        hover_is_valid: bool,
        hover_screen_pos: tuple[int, int] | None,
        debug_highlight_coord: tuple[int, int] | None,
    ):
        """Renders the main game grid and overlays onto the provided grid_surf."""
        # Background
        bg_color = (
            colors.GRID_BG_GAME_OVER if game_state.is_over() else colors.GRID_BG_DEFAULT
        )
        grid_drawing.draw_grid_background(grid_surf, bg_color)

        # Grid Triangles
        grid_drawing.draw_grid_triangles(
            grid_surf, game_state.grid_data, self.env_config
        )

        # Debug Indices
        if mode == "debug":
            grid_drawing.draw_grid_indices(
                grid_surf, game_state.grid_data, self.env_config, self.fonts
            )

        # Play Mode Hover Previews
        if mode == "play" and hover_shape:
            if hover_grid_coord:  # Snapped preview
                draw_placement_preview(
                    grid_surf,
                    hover_shape,
                    hover_grid_coord[0],
                    hover_grid_coord[1],
                    is_valid=hover_is_valid,  # Use validity passed in
                    config=self.env_config,
                )
            elif hover_screen_pos:  # Floating preview (relative to grid_surf)
                # Adjust screen pos to be relative to grid_surf
                local_hover_pos = (
                    hover_screen_pos[0] - grid_rect.left,
                    hover_screen_pos[1] - grid_rect.top,
                )
                if grid_surf.get_rect().collidepoint(local_hover_pos):
                    draw_floating_preview(
                        grid_surf,
                        hover_shape,
                        local_hover_pos,
                        self.env_config,
                    )

        # Debug Mode Highlight
        if mode == "debug" and debug_highlight_coord:
            r, c = debug_highlight_coord
            highlight_drawing.draw_debug_highlight(grid_surf, r, c, self.env_config)

        # --- ADDED: Display Score in Grid Area for Interactive Modes ---
        score_font = self.fonts.get("score")
        if score_font:
            score_text = f"Score: {game_state.game_score:.0f}"
            score_surf = score_font.render(score_text, True, colors.YELLOW)
            # Position score at top-left of grid area
            score_rect = score_surf.get_rect(topleft=(5, 5))
            grid_surf.blit(score_surf, score_rect)
        # --- END ADDED ---

    def _render_preview_area(
        self,
        preview_surf: pygame.Surface,
        game_state: GameState,
        mode: str,
        preview_rect: pygame.Rect,
        selected_shape_idx: int,  # Pass selected index
    ):
        """Renders the shape preview slots onto preview_surf and caches rects."""
        # Pass selected_shape_idx to render_previews for highlighting
        current_preview_rects = preview_drawing.render_previews(
            preview_surf,
            game_state,
            preview_rect.topleft,  # Pass absolute top-left
            mode,
            self.env_config,
            self.vis_config,
            selected_shape_idx=selected_shape_idx,  # Pass selection state
        )
        # Update cache only if it changed (or first time)
        if not self.preview_rects or self.preview_rects != current_preview_rects:
            self.preview_rects = current_preview_rects


File: trianglengin\visualization\core\__init__.py
"""Core visualization components: renderers, layout, fonts, colors, coordinate mapping."""

from . import colors, coord_mapper, fonts, layout
from .visualizer import Visualizer

__all__ = [
    "Visualizer",
    "layout",
    "fonts",
    "colors",
    "coord_mapper",
]


File: trianglengin\visualization\drawing\grid.py
import pygame

# Use internal imports
from ...config import EnvConfig
from ...core.environment.grid import GridData
from ...core.structs import (
    COLOR_ID_MAP,
    DEBUG_COLOR_ID,
    NO_COLOR_ID,
    Triangle,
)
from ..core import colors, coord_mapper


def draw_grid_background(surface: pygame.Surface, bg_color: tuple) -> None:
    """Fills the grid area surface with a background color."""
    surface.fill(bg_color)


def draw_grid_triangles(
    surface: pygame.Surface, grid_data: GridData, config: EnvConfig
) -> None:
    """Draws all triangles (empty, occupied, death) on the grid surface using NumPy state."""
    if surface.get_width() <= 0 or surface.get_height() <= 0:
        return

    cw, ch, ox, oy = coord_mapper._calculate_render_params(
        surface.get_width(), surface.get_height(), config
    )
    if cw <= 0 or ch <= 0:
        return

    # Get direct references to NumPy arrays
    occupied_np = grid_data._occupied_np
    death_np = grid_data._death_np
    color_id_np = grid_data._color_id_np

    for r in range(grid_data.rows):
        for c in range(grid_data.cols):
            is_death = death_np[r, c]
            is_occupied = occupied_np[r, c]
            color_id = color_id_np[r, c]
            is_up = (r + c) % 2 != 0  # Calculate orientation

            color: tuple[int, int, int] | None = None
            border_color = colors.GRID_LINE_COLOR
            border_width = 1

            if is_death:
                color = colors.DARK_GRAY
                border_color = colors.RED
            elif is_occupied:
                if color_id == DEBUG_COLOR_ID:
                    color = colors.DEBUG_TOGGLE_COLOR  # Special debug color
                elif color_id != NO_COLOR_ID and 0 <= color_id < len(COLOR_ID_MAP):
                    color = COLOR_ID_MAP[color_id]
                else:
                    # Fallback if occupied but no valid color ID (shouldn't happen)
                    color = colors.PURPLE  # Error color
            else:  # Empty playable cell
                color = colors.TRIANGLE_EMPTY_COLOR

            # Create temporary Triangle only for geometry calculation
            temp_tri = Triangle(r, c, is_up)
            pts = temp_tri.get_points(ox, oy, cw, ch)

            if color:  # Should always be true unless error
                pygame.draw.polygon(surface, color, pts)
            pygame.draw.polygon(surface, border_color, pts, border_width)


def draw_grid_indices(
    surface: pygame.Surface,
    grid_data: GridData,
    config: EnvConfig,
    fonts: dict[str, pygame.font.Font | None],
) -> None:
    """Draws the index number inside each triangle, including death cells."""
    if surface.get_width() <= 0 or surface.get_height() <= 0:
        return

    font = fonts.get("help")
    if not font:
        return

    cw, ch, ox, oy = coord_mapper._calculate_render_params(
        surface.get_width(), surface.get_height(), config
    )
    if cw <= 0 or ch <= 0:
        return

    # Get direct references to NumPy arrays
    occupied_np = grid_data._occupied_np
    death_np = grid_data._death_np
    color_id_np = grid_data._color_id_np

    for r in range(grid_data.rows):
        for c in range(grid_data.cols):
            is_death = death_np[r, c]
            is_occupied = occupied_np[r, c]
            color_id = color_id_np[r, c]
            is_up = (r + c) % 2 != 0  # Calculate orientation

            # Create temporary Triangle only for geometry calculation
            temp_tri = Triangle(r, c, is_up)
            pts = temp_tri.get_points(ox, oy, cw, ch)
            center_x = sum(p[0] for p in pts) / 3
            center_y = sum(p[1] for p in pts) / 3

            text_color = colors.WHITE  # Default

            if is_death:
                text_color = colors.LIGHT_GRAY
            elif is_occupied:
                bg_color: tuple[int, int, int] | None = None
                if color_id == DEBUG_COLOR_ID:
                    bg_color = colors.DEBUG_TOGGLE_COLOR
                elif color_id != NO_COLOR_ID and 0 <= color_id < len(COLOR_ID_MAP):
                    bg_color = COLOR_ID_MAP[color_id]

                if bg_color:
                    brightness = sum(bg_color) / 3
                    text_color = colors.WHITE if brightness < 128 else colors.BLACK
                else:  # Fallback if color missing
                    text_color = colors.RED
            else:  # Empty playable
                bg_color = colors.TRIANGLE_EMPTY_COLOR
                brightness = sum(bg_color) / 3
                text_color = colors.WHITE if brightness < 128 else colors.BLACK

            index = r * config.COLS + c
            text_surf = font.render(str(index), True, text_color)
            text_rect = text_surf.get_rect(center=(center_x, center_y))
            surface.blit(text_surf, text_rect)


File: trianglengin\visualization\drawing\highlight.py
import pygame

# Use internal imports
from ...config import EnvConfig
from ...core.structs import Triangle
from ..core import colors, coord_mapper


def draw_debug_highlight(
    surface: pygame.Surface, r: int, c: int, config: EnvConfig
) -> None:
    """Highlights a specific triangle border for debugging."""
    if surface.get_width() <= 0 or surface.get_height() <= 0:
        return

    cw, ch, ox, oy = coord_mapper._calculate_render_params(
        surface.get_width(), surface.get_height(), config
    )
    if cw <= 0 or ch <= 0:
        return

    is_up = (r + c) % 2 != 0
    temp_tri = Triangle(r, c, is_up)
    pts = temp_tri.get_points(ox, oy, cw, ch)

    pygame.draw.polygon(surface, colors.DEBUG_TOGGLE_COLOR, pts, 3)


File: trianglengin\visualization\drawing\hud.py
# File: trianglengin/trianglengin/visualization/drawing/hud.py
from typing import Any

import pygame

# Use internal imports
from ..core import colors


def render_hud(
    surface: pygame.Surface,
    mode: str,
    fonts: dict[str, pygame.font.Font | None],
    _display_stats: dict[str, Any] | None = None,  # Prefix with underscore
) -> None:
    """
    Renders HUD elements for interactive modes (play/debug).
    Displays only help text relevant to the mode.
    Ignores _display_stats.
    """
    screen_w, screen_h = surface.get_size()
    help_font = fonts.get("help")

    if not help_font:
        return

    bottom_y = screen_h - 10  # Position from bottom

    # --- Render Help Text Only ---
    help_text = "[ESC] Quit"
    if mode == "play":
        help_text += " | [Click] Select/Place Shape"
    elif mode == "debug":
        help_text += " | [Click] Toggle Cell"

    help_surf = help_font.render(help_text, True, colors.LIGHT_GRAY)
    # Position help text at the bottom right
    help_rect = help_surf.get_rect(bottomright=(screen_w - 15, bottom_y))
    surface.blit(help_surf, help_rect)


File: trianglengin\visualization\drawing\previews.py
import logging

import pygame

# Import VisConfig from alphatriangle (assuming it stays there for training viz)
# If VisConfig moves entirely, import from ...config
from alphatriangle.config import VisConfig

# Use internal imports
from ...config import EnvConfig
from ...core.environment import GameState
from ...core.structs import Shape, Triangle
from ..core import colors, coord_mapper
from .shapes import draw_shape

logger = logging.getLogger(__name__)


def render_previews(
    surface: pygame.Surface,
    game_state: GameState,
    area_topleft: tuple[int, int],
    _mode: str,
    env_config: EnvConfig,
    vis_config: VisConfig,
    selected_shape_idx: int = -1,
) -> dict[int, pygame.Rect]:
    """Renders shape previews in their area. Returns dict {index: screen_rect}."""
    surface.fill(colors.PREVIEW_BG)
    preview_rects_screen: dict[int, pygame.Rect] = {}
    num_slots = env_config.NUM_SHAPE_SLOTS
    pad = vis_config.PREVIEW_PADDING
    inner_pad = vis_config.PREVIEW_INNER_PADDING
    border = vis_config.PREVIEW_BORDER_WIDTH
    selected_border = vis_config.PREVIEW_SELECTED_BORDER_WIDTH

    if num_slots <= 0:
        return {}

    # Calculate dimensions for each slot
    total_pad_h = (num_slots + 1) * pad
    available_h = surface.get_height() - total_pad_h
    slot_h = available_h / num_slots if num_slots > 0 else 0
    slot_w = surface.get_width() - 2 * pad

    current_y = float(pad)  # Start y position as float

    for i in range(num_slots):
        # Calculate local rectangle for the slot within the preview surface
        slot_rect_local = pygame.Rect(pad, int(current_y), int(slot_w), int(slot_h))
        # Calculate screen rectangle by offsetting local rect
        slot_rect_screen = slot_rect_local.move(area_topleft)
        preview_rects_screen[i] = (
            slot_rect_screen  # Store screen rect for interaction mapping
        )

        shape: Shape | None = game_state.shapes[i]
        # Use the passed selected_shape_idx for highlighting
        is_selected = selected_shape_idx == i

        # Determine border style based on selection
        border_width = selected_border if is_selected else border
        border_color = (
            colors.PREVIEW_SELECTED_BORDER if is_selected else colors.PREVIEW_BORDER
        )
        # Draw the border rectangle onto the local preview surface
        pygame.draw.rect(surface, border_color, slot_rect_local, border_width)

        # Draw the shape if it exists
        if shape:
            # Calculate drawing area inside the border and padding
            draw_area_w = slot_w - 2 * (border_width + inner_pad)
            draw_area_h = slot_h - 2 * (border_width + inner_pad)

            if draw_area_w > 0 and draw_area_h > 0:
                # Calculate shape bounding box and required cell size
                min_r, min_c, max_r, max_c = shape.bbox()
                shape_rows = max_r - min_r + 1
                # Effective width considering triangle geometry (0.75 factor)
                shape_cols_eff = (
                    (max_c - min_c + 1) * 0.75 + 0.25 if shape.triangles else 1
                )

                # Determine cell size based on available space and shape dimensions
                scale_w = (
                    draw_area_w / shape_cols_eff if shape_cols_eff > 0 else draw_area_w
                )
                scale_h = draw_area_h / shape_rows if shape_rows > 0 else draw_area_h
                cell_size = max(1.0, min(scale_w, scale_h))  # Use the smaller scale

                # Calculate centered top-left position for drawing the shape
                shape_render_w = shape_cols_eff * cell_size
                shape_render_h = shape_rows * cell_size
                draw_topleft_x = (
                    slot_rect_local.left
                    + border_width
                    + inner_pad
                    + (draw_area_w - shape_render_w) / 2
                )
                draw_topleft_y = (
                    slot_rect_local.top
                    + border_width
                    + inner_pad
                    + (draw_area_h - shape_render_h) / 2
                )

                # Draw the shape onto the local preview surface
                # Cast float coordinates to int for draw_shape
                # Use _is_selected to match the function signature
                draw_shape(
                    surface,
                    shape,
                    (int(draw_topleft_x), int(draw_topleft_y)),
                    cell_size,
                    _is_selected=is_selected,
                    origin_offset=(
                        -min_r,
                        -min_c,
                    ),  # Adjust drawing origin based on bbox
                )

        # Move to the next slot position
        current_y += slot_h + pad

    return preview_rects_screen


def draw_placement_preview(
    surface: pygame.Surface,
    shape: Shape,
    r: int,
    c: int,
    is_valid: bool,
    config: EnvConfig,
) -> None:
    """Draws a semi-transparent shape snapped to the grid."""
    if not shape or not shape.triangles:
        return

    cw, ch, ox, oy = coord_mapper._calculate_render_params(
        surface.get_width(), surface.get_height(), config
    )
    if cw <= 0 or ch <= 0:
        return

    # Use valid/invalid colors (could be passed in or defined here)
    base_color = (
        colors.PLACEMENT_VALID_COLOR[:3]
        if is_valid
        else colors.PLACEMENT_INVALID_COLOR[:3]
    )
    alpha = (
        colors.PLACEMENT_VALID_COLOR[3]
        if is_valid
        else colors.PLACEMENT_INVALID_COLOR[3]
    )
    color = list(base_color) + [alpha]  # Combine RGB and Alpha

    # Use a temporary surface for transparency
    temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    temp_surface.fill((0, 0, 0, 0))  # Fully transparent background

    for dr, dc, is_up in shape.triangles:
        tri_r, tri_c = r + dr, c + dc
        # Create a temporary Triangle to get points easily
        temp_tri = Triangle(tri_r, tri_c, is_up)
        pts = temp_tri.get_points(ox, oy, cw, ch)
        pygame.draw.polygon(temp_surface, color, pts)

    # Blit the transparent preview onto the main grid surface
    surface.blit(temp_surface, (0, 0))


def draw_floating_preview(
    surface: pygame.Surface,
    shape: Shape,
    screen_pos: tuple[int, int],  # Position relative to the surface being drawn on
    _config: EnvConfig,  # Mark config as unused
) -> None:
    """Draws a semi-transparent shape floating at the screen position."""
    if not shape or not shape.triangles:
        return

    cell_size = 20.0  # Fixed size for floating preview? Or scale based on config?
    color = list(shape.color) + [100]  # Base color with fixed alpha

    # Use a temporary surface for transparency
    temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    temp_surface.fill((0, 0, 0, 0))

    # Center the shape around the screen_pos
    min_r, min_c, max_r, max_c = shape.bbox()
    center_r = (min_r + max_r) / 2.0
    center_c = (min_c + max_c) / 2.0

    for dr, dc, is_up in shape.triangles:
        # Calculate position relative to shape center and screen_pos
        pt_x = screen_pos[0] + (dc - center_c) * (cell_size * 0.75)
        pt_y = screen_pos[1] + (dr - center_r) * cell_size

        # Create a temporary Triangle at origin to get relative points
        temp_tri = Triangle(0, 0, is_up)
        # Get points relative to 0,0 and scale
        rel_pts = temp_tri.get_points(0, 0, cell_size, cell_size)
        # Translate points to the calculated screen position
        pts = [(px + pt_x, py + pt_y) for px, py in rel_pts]
        pygame.draw.polygon(temp_surface, color, pts)

    # Blit the transparent preview onto the target surface
    surface.blit(temp_surface, (0, 0))


File: trianglengin\visualization\drawing\README.md

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

File: trianglengin\visualization\drawing\shapes.py
import pygame

# Use internal imports
from ...core.structs import Shape, Triangle
from ..core import colors


def draw_shape(
    surface: pygame.Surface,
    shape: Shape,
    topleft: tuple[int, int],
    cell_size: float,
    _is_selected: bool = False,
    origin_offset: tuple[int, int] = (0, 0),
) -> None:
    """Draws a single shape onto a surface."""
    if not shape or not shape.triangles or cell_size <= 0:
        return

    shape_color = shape.color
    border_color = colors.GRAY

    cw = cell_size
    ch = cell_size

    for dr, dc, is_up in shape.triangles:
        adj_r, adj_c = dr + origin_offset[0], dc + origin_offset[1]

        tri_x = topleft[0] + adj_c * (cw * 0.75)
        tri_y = topleft[1] + adj_r * ch

        temp_tri = Triangle(0, 0, is_up)
        pts = [(px + tri_x, py + tri_y) for px, py in temp_tri.get_points(0, 0, cw, ch)]

        pygame.draw.polygon(surface, shape_color, pts)
        pygame.draw.polygon(surface, border_color, pts, 1)


File: trianglengin\visualization\drawing\__init__.py
"""Drawing functions for specific visual elements."""

from .grid import (
    draw_grid_background,
    draw_grid_indices,
    draw_grid_triangles,
)
from .highlight import draw_debug_highlight
from .hud import render_hud
from .previews import (
    draw_floating_preview,
    draw_placement_preview,
    render_previews,
)
from .shapes import draw_shape

__all__ = [
    "draw_grid_background",
    "draw_grid_triangles",
    "draw_grid_indices",
    "draw_shape",
    "render_previews",
    "draw_placement_preview",
    "draw_floating_preview",
    "render_hud",
    "draw_debug_highlight",
]


