
[![CI Status](https://github.com/lguibr/alphatriangle/actions/workflows/trianglengin_ci_cd.yml/badge.svg)](https://github.com/lguibr/alphatriangle/actions/workflows/trianglengin_ci_cd.yml) <!-- Update workflow name if changed -->
[![codecov](https://codecov.io/gh/lguibr/alphatriangle/graph/badge.svg?token=YOUR_CODECOV_TOKEN_HERE&flag=trianglengin)](https://codecov.io/gh/lguibr/alphatriangle) <!-- Added Codecov badge -->
[![PyPI version](https://badge.fury.io/py/trianglengin.svg)](https://badge.fury.io/py/trianglengin)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)


# Triangle Engine (`trianglengin`)

This library provides the core, reusable components for reinforcement learning agents playing a triangle puzzle game, specifically designed for use by the [AlphaTriangle](https://github.com/lguibr/alphatriangle) and potentially MuzeroTriangle projects.

It encapsulates:

1.  **Core Game Logic:** Environment rules, state representation, actions.
2.  **Utilities:** General helpers, SumTree, geometry functions, shared types (Planned).
3.  **Statistics Collection:** The `StatsCollectorActor` (Planned).
4.  **Feature Extraction:** Logic to convert game state to NN input format (Planned).
5.  **Data Management Framework:** Structure for saving/loading checkpoints and buffers (Planned).

## Purpose

The primary goal is to avoid code duplication between different RL agent implementations (like AlphaZero and MuZero) that operate on the same underlying game environment. By extracting the common backend logic into this installable library, the main agent projects can focus solely on their specific algorithms (MCTS variations, NN architectures, training loops).

## Installation

```bash
# For development (from the trianglengin root directory):
pip install -e .[dev]

# For standard use (once published or built):
pip install trianglengin
```

## Local Development & Testing

1.  **Setup:**
    *   Clone the repository.
    *   Create and activate a virtual environment (`python -m venv venv && source venv/bin/activate`).
    *   Install in editable mode with development dependencies: `pip install -e .[dev]`

2.  **Running Checks:**
    *   **Tests & Coverage:** `pytest tests/ --cov=trianglengin --cov-report=xml` (Generates `coverage.xml` for upload)
    *   **Linting:** `ruff check .`
    *   **Formatting:** `ruff format .`
    *   **Type Checking:** `mypy trianglengin/`

## Project Structure

```
trianglengin/
├── .github/workflows/      # GitHub Actions CI/CD
│   └── trianglengin_ci_cd.yml
├── trianglengin/           # Source code for the library package
│   ├── __init__.py         # Exposes public API
│   ├── core/               # Core game logic
│   │   ├── __init__.py
│   │   ├── structs/        # Triangle, Shape, constants
│   │   │   └── README.md
│   │   └── environment/    # GameState, GridData, GridLogic, ShapeLogic, ActionCodec
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

## Core Components (Phase 1)

*   **`trianglengin.core`**: Contains the fundamental game logic.
    *   **`structs`**: Defines `Triangle`, `Shape`, and related constants (`SHAPE_COLORS`, `COLOR_ID_MAP`, etc.). See [`trianglengin/core/structs/README.md`](trianglengin/core/structs/README.md).
    *   **`environment`**: Defines the `GameState`, `GridData`, `GridLogic`, `ShapeLogic`, action encoding/decoding, and step execution logic. See [`trianglengin/core/environment/README.md`](trianglengin/core/environment/README.md).
*   **`trianglengin.config`**: Contains shared configuration models.
    *   `EnvConfig`: Pydantic model for environment parameters.

## Future Phases

Subsequent phases will integrate:

*   Utilities (`utils`)
*   Statistics Collection (`stats`)
*   Feature Extraction (`features`)
*   Data Management (`data`)

## Contributing

Please refer to the main [AlphaTriangle repository](https://github.com/lguibr/alphatriangle) for contribution guidelines. Ensure that changes here remain compatible with the projects using this library. Keep READMEs updated.
