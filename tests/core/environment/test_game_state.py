# File: trianglengin/tests/core/environment/test_game_state.py
# Extracted logic from various alphatriangle tests
import numpy as np  # <-- ADDED IMPORT
import pytest

# Import directly from the library being tested
from trianglengin.core.environment import GameState, encode_action

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
    if valid_actions:
        game_state.step(valid_actions[0])
        game_state.step(valid_actions[1 % len(valid_actions)])
    assert game_state.current_step > 0 or not valid_actions

    game_state.reset()

    assert game_state.current_step == 0
    assert game_state.game_score == 0.0
    assert not game_state.is_over()
    assert len(game_state.shapes) == game_state.env_config.NUM_SHAPE_SLOTS
    assert all(s is not None for s in game_state.shapes)  # Should be refilled
    if game_state.env_config.ROWS > 0 and game_state.env_config.COLS > 0:
        assert len(game_state.valid_actions()) > 0


def test_game_state_step(game_state_with_fixed_shapes: GameState):
    """Test a valid step."""
    gs = game_state_with_fixed_shapes
    initial_score = gs.game_score
    initial_step = gs.current_step
    shape_idx = 0
    r, c = 2, 2  # Assuming this is a valid placement for shape 0
    action = encode_action(shape_idx, r, c, gs.env_config)

    # Ensure the action is valid before stepping
    assert action in gs.valid_actions()

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
    r, c = 2, 2
    gs.grid_data._occupied_np[r, c] = True
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
            assert copy_state.shapes[i] == game_state.shapes[i]

    # Modify copy and check original is unchanged
    copy_state.game_score += 100
    assert game_state.game_score != copy_state.game_score
    if copy_state.shapes[0]:
        copy_state.shapes[0].color = (1, 1, 1)
        if game_state.shapes[0]:
            assert game_state.shapes[0].color != (1, 1, 1)
    copy_state.grid_data._occupied_np[0, 0] = not copy_state.grid_data._occupied_np[
        0, 0
    ]
    assert (
        game_state.grid_data._occupied_np[0, 0]
        != copy_state.grid_data._occupied_np[0, 0]
    )
