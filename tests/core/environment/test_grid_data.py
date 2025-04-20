# File: tests/core/environment/test_grid_data.py
import numpy as np
import pytest

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
    """Test _precompute_lines with a non-default, simple config."""
    # Simple 3x3 fully playable grid, min line length 2
    config = EnvConfig(ROWS=3, COLS=3, COLS_PER_ROW=[3, 3, 3], MIN_LINE_LENGTH=2)
    lines = _precompute_lines(config)

    # Convert to sets of frozensets for easier comparison
    line_sets = {frozenset(line) for line in lines}

    # Expected HORIZONTAL lines (length >= 2) in a 3x3 grid:
    expected_h = (
        {frozenset([(r, 0), (r, 1)]) for r in range(3)}  # Len 2
        | {frozenset([(r, 1), (r, 2)]) for r in range(3)}  # Len 2
        | {frozenset([(r, 0), (r, 1), (r, 2)]) for r in range(3)}  # Len 3
    )

    # Expected DIAGONAL TL-BR lines (length >= 2) in a 3x3 grid:
    # (0,1)T -> (1,1)F
    # (0,2)T -> (1,2)F
    # (1,0)F -> (1,1)T
    # (1,1)T -> (2,1)F
    # (1,2)F -> (2,2)T (Invalid T) -> (2,2)F
    # (0,1)T -> (1,1)F -> (1,2)T (Invalid T) -> (1,2)F
    # (1,0)F -> (1,1)T -> (2,1)F
    expected_d1 = {
        frozenset([(0, 1), (1, 1)]),
        frozenset([(0, 2), (1, 2)]),
        frozenset([(1, 0), (1, 1)]),
        frozenset([(1, 1), (2, 1)]),
        frozenset([(1, 2), (2, 2)]),
        frozenset([(0, 1), (1, 1), (1, 2)]),  # Len 3
        frozenset([(1, 0), (1, 1), (2, 1)]),  # Len 3
    }

    # Expected DIAGONAL BL-TR lines (length >= 2) in a 3x3 grid:
    # (1,0)F -> (0,0)T (Invalid T) -> (0,0)F
    # (1,1)T -> (0,1)F (Invalid F) -> (0,1)T
    # (1,2)F -> (0,2)T
    # (2,0)F -> (1,0)T (Invalid T) -> (1,0)F
    # (2,1)F -> (1,1)T
    # (2,2)F -> (1,2)T (Invalid T) -> (1,2)F
    # (1,0)F -> (0,1)T
    # (1,1)T -> (0,2)F (Invalid F) -> (0,2)T
    # (2,0)F -> (1,1)T
    # (2,1)F -> (1,2)T
    # (1,0)F -> (0,1)T -> (0,2)F (Invalid F) -> (0,2)T
    # (2,0)F -> (1,1)T -> (0,2)T
    expected_d2 = {
        frozenset([(1, 0), (0, 0)]),
        frozenset([(1, 1), (0, 1)]),
        frozenset([(1, 2), (0, 2)]),
        frozenset([(2, 0), (1, 0)]),
        frozenset([(2, 1), (1, 1)]),
        frozenset([(2, 2), (1, 2)]),
        frozenset([(1, 0), (0, 1)]),
        frozenset([(1, 1), (0, 2)]),
        frozenset([(2, 0), (1, 1)]),
        frozenset([(2, 1), (1, 2)]),
        frozenset([(1, 0), (0, 1), (0, 2)]),  # Len 3
        frozenset([(2, 0), (1, 1), (0, 2)]),  # Len 3
    }

    # Combine all expected lines
    expected_lines = expected_h | expected_d1 | expected_d2
    assert line_sets == expected_lines
    assert len(lines) == len(expected_lines)
