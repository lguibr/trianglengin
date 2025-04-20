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
        for c_try in range(s, e):  # Iterate only through playable columns
            if GridLogic.can_place(grid_data, simple_shape, r, c_try):
                start_r, start_c = r, c_try
                break
        if start_r != -1:
            break  # Found a spot
    if start_r == -1:
        pytest.skip("Could not find valid placement for simple_shape in empty grid.")

    assert GridLogic.can_place(grid_data, simple_shape, start_r, start_c)


def test_can_place_occupied(grid_data: GridData, simple_shape: Shape):
    """Test placement fails if any target cell is occupied."""
    start_r, start_c = -1, -1
    for r in range(grid_data.rows):
        s, e = grid_data.config.PLAYABLE_RANGE_PER_ROW[r]
        for c_try in range(s, e):
            if GridLogic.can_place(grid_data, simple_shape, r, c_try):
                start_r, start_c = r, c_try
                break
        if start_r != -1:
            break
    if start_r == -1:
        pytest.skip("Could not find valid placement for simple_shape.")

    # Occupy one of the cells the shape would cover
    shape_target_coords = set()
    for dr, dc, _ in simple_shape.triangles:
        shape_target_coords.add((start_r + dr, start_c + dc))

    # Find a valid coord within the shape to occupy
    coord_to_occupy = None
    for r_occ, c_occ in shape_target_coords:
        if grid_data.valid(r_occ, c_occ) and not grid_data.is_death(r_occ, c_occ):
            coord_to_occupy = (r_occ, c_occ)
            break

    if coord_to_occupy:
        grid_data._occupied_np[coord_to_occupy[0], coord_to_occupy[1]] = True
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
        pytest.skip("Could not find a death zone cell.")

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
        for c in range(s, e, 3):  # Place sparsely
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
    for r_occ, c_occ in coords_to_occupy:
        assert grid_data._occupied_np[r_occ, c_occ]


def test_check_and_clear_lines_single_line(grid_data: GridData):
    """Test clearing a single maximal line."""
    # Find any precomputed maximal line
    if not grid_data._lines:
        pytest.skip("No precomputed lines found for this configuration.")

    # Select the first maximal line found
    target_line_coords_tuple = grid_data._lines[0]
    expected_line_coords_fs = frozenset(target_line_coords_tuple)

    # Occupy all but the last coordinate in the line
    coords_list = list(target_line_coords_tuple)
    if not coords_list:
        pytest.skip("Selected line is empty.")

    last_coord = coords_list[-1]
    coords_to_pre_occupy = set(coords_list[:-1])
    occupy_coords(grid_data, coords_to_pre_occupy)

    # Occupy the last coordinate
    newly_occupied = {last_coord}
    occupy_coords(grid_data, newly_occupied)

    # Check for clears
    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )

    assert lines_cleared >= 1  # Could clear more than one if lines overlap
    assert unique_cleared.issuperset(expected_line_coords_fs)
    assert expected_line_coords_fs in cleared_lines_set

    # Verify the cleared coordinates are no longer occupied
    for r_clr, c_clr in expected_line_coords_fs:
        assert not grid_data._occupied_np[r_clr, c_clr]


def test_check_and_clear_lines_no_lines_to_check(grid_data: GridData):
    """Test the case where newly occupied coords are not part of any potential line."""
    # Find a coordinate not in the map (e.g., a death zone coord if possible)
    coord_not_in_map = None
    for r in range(grid_data.rows):
        for c in range(grid_data.cols):
            if (r, c) not in grid_data._coord_to_lines_map:
                coord_not_in_map = (r, c)
                break
        if coord_not_in_map:
            break

    if coord_not_in_map is None:
        pytest.skip("Could not find a coordinate not in the line map.")

    newly_occupied = {coord_not_in_map}
    # Manually occupy it for the test (even if it's death zone, logic should handle)
    if grid_data.valid(*coord_not_in_map):
        grid_data._occupied_np[coord_not_in_map] = True

    lines_cleared, unique_cleared, cleared_lines_set = GridLogic.check_and_clear_lines(
        grid_data, newly_occupied
    )
    assert lines_cleared == 0
    assert not unique_cleared
    assert not cleared_lines_set
