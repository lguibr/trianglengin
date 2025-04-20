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
