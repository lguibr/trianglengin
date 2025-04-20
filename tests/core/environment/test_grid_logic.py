# File: tests/core/environment/test_grid_logic.py
import pytest

# Import directly from the library being tested
from trianglengin.core.environment.grid import GridData
from trianglengin.core.environment.grid import logic as GridLogic
from trianglengin.core.structs import Shape

# Use fixtures from the local conftest.py
# Fixtures are implicitly injected by pytest


# --- Test can_place with NumPy GridData ---
def test_can_place_empty_grid(grid_data: GridData, simple_shape: Shape):
    """Test placement on an empty grid."""
    start_r, start_c = -1, -1
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        # Combine checks using 'and'
        if s < e and GridLogic.can_place(grid_data, simple_shape, r, s):
            start_r, start_c = r, s
            break
        if start_r != -1:
            break
    if start_r == -1:
        pytest.skip("Could not find valid placement for simple_shape in empty grid.")

    assert GridLogic.can_place(grid_data, simple_shape, start_r, start_c)


def test_can_place_occupied(grid_data: GridData, simple_shape: Shape):
    """Test placement fails if any target cell is occupied."""
    start_r, start_c = -1, -1
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        if s < e and GridLogic.can_place(grid_data, simple_shape, r, s):
            start_r, start_c = r, s
            break
        if start_r != -1:
            break
    if start_r == -1:
        pytest.skip("Could not find valid placement for simple_shape.")

    target_r, target_c = start_r + 1, start_c + 1
    if grid_data.valid(target_r, target_c) and not grid_data.is_death(
        target_r, target_c
    ):
        grid_data._occupied_np[target_r, target_c] = True
        assert not GridLogic.can_place(grid_data, simple_shape, start_r, start_c)
    else:
        pytest.skip("Target cell for occupation is invalid or death zone.")


def test_can_place_death_zone(grid_data: GridData):
    """Test placement fails if any target cell is in a death zone."""
    death_r, death_c = -1, -1
    for r in range(grid_data.rows):
        start_col, end_col = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        if start_col > 0:
            death_r, death_c = r, start_col - 1
            break
        if end_col < grid_data.cols:
            death_r, death_c = r, end_col
            break
    if death_r == -1:
        pytest.skip("Could not find a death zone cell in this config.")

    assert grid_data.is_death(death_r, death_c)
    is_up_needed = (death_r + death_c) % 2 != 0
    single_tri_shape = Shape([(0, 0, is_up_needed)], (255, 0, 0))
    assert not GridLogic.can_place(grid_data, single_tri_shape, death_r, death_c)


def test_can_place_orientation_mismatch(grid_data: GridData):
    """Test placement fails if triangle orientations don't match."""
    up_r, up_c = -1, -1
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        for c in range(s, e):
            if (r + c) % 2 != 0:
                up_r, up_c = r, c
                break
        if up_r != -1:
            break
    if up_r == -1:
        pytest.skip("Could not find playable UP cell.")

    down_r, down_c = -1, -1
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        for c in range(s, e):
            if (r + c) % 2 == 0:
                down_r, down_c = r, c
                break
        if down_r != -1:
            break
    if down_r == -1:
        pytest.skip("Could not find playable DOWN cell.")

    shape_up = Shape([(0, 0, True)], (0, 255, 0))
    shape_down = Shape([(0, 0, False)], (255, 0, 0))

    assert not GridLogic.can_place(grid_data, shape_up, down_r, down_c)
    assert not GridLogic.can_place(grid_data, shape_down, up_r, up_c)

    assert GridLogic.can_place(grid_data, shape_down, down_r, down_c)
    assert GridLogic.can_place(grid_data, shape_up, up_r, up_c)


# --- Test check_and_clear_lines with NumPy GridData ---


def occupy_coords(grid_data: GridData, coords: set[tuple[int, int]]):
    """Helper to occupy specific coordinates."""
    for r, c in coords:
        if grid_data.valid(r, c) and not grid_data.is_death(r, c):
            grid_data._occupied_np[r, c] = True


def test_check_and_clear_lines_no_clear(grid_data: GridData):
    """Test when newly occupied cells don't complete any lines."""
    coords_to_occupy = set()
    count = 0
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        for c in range(s, e, 3):
            coords_to_occupy.add((r, c))
            count += 1
            if count >= 3:
                break
        if count >= 3:
            break
    if count < 3:
        pytest.skip("Could not find 3 suitable cells.")

    occupy_coords(grid_data, coords_to_occupy)
    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, coords_to_occupy
    )
    assert lines_cleared == 0
    assert not unique_cleared
    assert not cleared_lines_set
    for r, c in coords_to_occupy:
        assert grid_data._occupied_np[r, c]


def test_check_and_clear_lines_single_line(grid_data: GridData):
    """Test clearing a single horizontal line."""
    expected_line_coords_tuple = None
    target_row = grid_data.rows // 2
    for line_tuple in grid_data._lines:
        coords = list(line_tuple)
        if len(coords) >= grid_data.config.MIN_LINE_LENGTH and all(
            r == target_row for r, c in coords
        ):
            expected_line_coords_tuple = line_tuple
            break

    if not expected_line_coords_tuple:
        pytest.skip(
            f"Could not find a suitable horizontal line in row {target_row} for testing"
        )

    expected_line_coords = frozenset(expected_line_coords_tuple)
    coords_list = list(expected_line_coords_tuple)

    occupy_coords(grid_data, set(coords_list[:-1]))
    last_coord = coords_list[-1]
    newly_occupied = {last_coord}
    occupy_coords(grid_data, newly_occupied)

    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )

    assert lines_cleared == 1
    assert unique_cleared == set(expected_line_coords)
    assert expected_line_coords in cleared_lines_set
    assert len(cleared_lines_set) == 1

    for r, c in expected_line_coords:
        assert not grid_data._occupied_np[r, c]


def test_check_and_clear_lines_no_lines_to_check(grid_data: GridData):
    """Test the case where newly occupied coords are not part of any potential line."""
    death_r, death_c = -1, -1
    for r in range(grid_data.rows):
        start_col, end_col = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        if start_col > 0:
            death_r, death_c = r, start_col - 1
            break
        if end_col < grid_data.cols:
            death_r, death_c = r, end_col
            break
    if death_r == -1:
        pytest.skip("Could not find a death zone cell for test.")

    newly_occupied = {(death_r, death_c)}
    assert (death_r, death_c) not in grid_data._coord_to_lines_map

    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )
    assert lines_cleared == 0
    assert not unique_cleared
    assert not cleared_lines_set
