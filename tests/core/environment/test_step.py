# File: tests/core/environment/test_step.py
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

    # Remove unused mock_rng
    reward = execute_placement(gs, shape_idx, r, c)

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

    # Remove unused mock_rng
    reward = execute_placement(gs, shape_idx, r, c)

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
    # Remove unused mock_rng

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
    execute_placement(gs, p1["idx"], p1["r"], p1["c"])
    (p1["count"] * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE)
    # Allow for potential line clears in first step
    # assert reward1 == pytest.approx(expected_reward1)
    assert gs.shapes[p1["idx"]] is None
    assert gs.shapes[placements[1]["idx"]] is not None  # Check other slots remain
    assert gs.shapes[placements[2]["idx"]] is not None

    # Place second shape
    p2 = placements[1]
    execute_placement(gs, p2["idx"], p2["r"], p2["c"])
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
    reward3 = execute_placement(gs, p3["idx"], p3["r"], p3["c"])
    expected_reward3 = (
        p3["count"] * config.REWARD_PER_PLACED_TRIANGLE + config.REWARD_PER_STEP_ALIVE
    )  # Game not over yet, no lines cleared due to mock
    assert reward3 == pytest.approx(expected_reward3)
    mock_clear.assert_called_once()  # Verify mock was used
    sleep(0.01)  # Allow time for refill to happen (though it should be synchronous)

    # --- Verify REFILL happened ---
    assert all(s is not None for s in gs.shapes), "Not all slots were refilled"
    # Check that shapes are different (probabilistically)
    assert (
        gs.shapes != initial_shapes_copy
    ), "Shapes after refill are identical to initial shapes (unlikely)"

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
    # Remove unused mock_rng

    # --- Mock check_and_clear_lines ---
    # Patch the function within the logic module where execute_placement imports it from
    mock_clear = mocker.patch(
        "trianglengin.core.environment.grid.logic.check_and_clear_lines",
        return_value=(0, set(), set()),  # Simulate no lines cleared
    )
    # --- End Mock ---

    # Execute placement - this should fill the last spot and trigger game over
    reward = execute_placement(game_state, shape_idx, empty_r, empty_c)

    # Verify the mock was called (optional but good practice)
    mock_clear.assert_called_once()

    # Verify game is over
    # The game over check happens *after* execute_placement in game_state.step
    # We need to manually check the condition here or call valid_actions
    if not game_state.valid_actions():
        game_state.game_over = True

    assert (
        game_state.is_over()
    ), "Game should be over after placing the final piece with no other valid moves"

    # Verify reward (placement + game over penalty)
    expected_reward = (
        placed_count * config.REWARD_PER_PLACED_TRIANGLE + config.PENALTY_GAME_OVER
    )
    # Use a slightly larger tolerance if needed, but approx should work
    assert reward == pytest.approx(expected_reward)
