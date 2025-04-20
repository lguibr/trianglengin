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
