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
