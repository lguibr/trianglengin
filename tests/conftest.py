# File: trianglengin/tests/conftest.py
import random
from typing import TYPE_CHECKING  # <-- ADDED IMPORT

import numpy as np
import pytest

# Import directly from the library being tested
from trianglengin.config import EnvConfig
from trianglengin.core.environment import GameState
from trianglengin.core.structs import Shape

# --- ADDED TYPE_CHECKING BLOCK ---
if TYPE_CHECKING:
    from trianglengin.core.environment.grid import GridData
# --- END ADDED ---


# Use default NumPy random number generator
rng = np.random.default_rng()


@pytest.fixture(scope="session")
def default_env_config() -> EnvConfig:
    """Provides the default EnvConfig used in the specification (session-scoped)."""
    # Pydantic models with defaults can be instantiated without args
    return EnvConfig()


@pytest.fixture
def game_state(default_env_config: EnvConfig) -> GameState:
    """Provides a fresh GameState instance for testing."""
    # Use a fixed seed for reproducibility within tests if needed
    return GameState(config=default_env_config, initial_seed=123)


@pytest.fixture
def game_state_with_fixed_shapes(default_env_config: EnvConfig) -> GameState:
    """
    Provides a game state with predictable initial shapes.
    Uses a modified EnvConfig with NUM_SHAPE_SLOTS=3 for this specific fixture.
    """
    # Create a specific config for this fixture
    config_3_slots = default_env_config.model_copy(update={"NUM_SHAPE_SLOTS": 3})
    gs = GameState(config=config_3_slots, initial_seed=456)

    # Override the random shapes with fixed ones for testing placement/refill
    fixed_shapes = [
        Shape([(0, 0, False)], (255, 0, 0)),  # Single down (matches grid at 0,0)
        Shape([(0, 0, True)], (0, 255, 0)),  # Single up (matches grid at 0,1)
        Shape(
            [(0, 0, False), (0, 1, True)], (0, 0, 255)
        ),  # Domino (matches grid at 0,0 and 0,1)
    ]
    # This fixture now guarantees NUM_SHAPE_SLOTS is 3
    assert len(fixed_shapes) == gs.env_config.NUM_SHAPE_SLOTS

    for i in range(len(fixed_shapes)):
        gs.shapes[i] = fixed_shapes[i]
    return gs


@pytest.fixture
def simple_shape() -> Shape:
    """Provides a simple 3-triangle shape (Down, Up, Down)."""
    # Example: L-shape (Down at 0,0; Up at 1,0; Down at 1,1 relative)
    # Grid at (r,c) is Down if r+c is even, Up if odd.
    # (0,0) is Down. (1,0) is Up. (1,1) is Down. This shape matches grid orientation.
    triangles = [(0, 0, False), (1, 0, True), (1, 1, False)]
    color = (255, 0, 0)
    return Shape(triangles, color)


@pytest.fixture
def grid_data(default_env_config: EnvConfig) -> "GridData":
    """Provides a fresh GridData instance."""
    # Import GridData locally to avoid potential circular dependency at module level
    from trianglengin.core.environment.grid import GridData

    return GridData(config=default_env_config)


@pytest.fixture
def game_state_almost_full(default_env_config: EnvConfig) -> GameState:
    """
    Provides a game state where only a few placements are possible.
    Grid is filled completely, then specific spots are made empty.
    """
    # Use a fresh GameState to avoid side effects from other tests using the shared 'game_state' fixture
    gs = GameState(config=default_env_config, initial_seed=987)
    # Fill the entire playable grid first using NumPy arrays
    playable_mask = ~gs.grid_data._death_np
    gs.grid_data._occupied_np[playable_mask] = True

    # Explicitly make specific spots empty: (0,4) [Down] and (0,5) [Up]
    empty_spots = [(0, 4), (0, 5)]
    for r_empty, c_empty in empty_spots:
        if gs.grid_data.valid(r_empty, c_empty):
            gs.grid_data._occupied_np[r_empty, c_empty] = False
            # Reset color ID as well
            gs.grid_data._color_id_np[
                r_empty, c_empty
            ] = -1  # Assuming -1 is NO_COLOR_ID
    return gs


@pytest.fixture
def fixed_rng() -> random.Random:
    """Provides a Random instance with a fixed seed."""
    return random.Random(12345)
