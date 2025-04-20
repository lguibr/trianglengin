# File: tests/core/environment/test_game_state.py
import copy
import logging

import numpy as np
import pytest
from pytest_mock import MockerFixture

import trianglengin.core.environment.grid.logic as GridLogic
from trianglengin.config.env_config import EnvConfig
from trianglengin.core.environment.action_codec import (
    ActionType,
    decode_action,
    encode_action,
)
from trianglengin.core.environment.game_state import GameState
from trianglengin.core.structs.shape import Shape
from trianglengin.visualization.core.colors import Color

# Configure logging for tests
logging.basicConfig(level=logging.INFO)  # Set to INFO to reduce noise unless debugging

# Define a default color for shapes in tests
DEFAULT_TEST_COLOR: Color = (100, 100, 100)


@pytest.fixture
def default_config() -> EnvConfig:
    """Fixture for default environment configuration."""
    return EnvConfig()


@pytest.fixture
def default_game_state(default_config: EnvConfig) -> GameState:
    """Fixture for a default GameState."""
    return GameState(config=default_config, initial_seed=123)  # Use fixed seed


@pytest.fixture
def game_state_with_fixed_shapes() -> GameState:
    """Fixture for a GameState with predictable shapes for testing."""
    # Create a new GameState directly with the test config
    test_config = EnvConfig(
        ROWS=3,
        COLS=3,
        PLAYABLE_RANGE_PER_ROW=[(0, 3), (0, 3), (0, 3)],  # Full 3x3 is playable
        NUM_SHAPE_SLOTS=3,
        MIN_LINE_LENGTH=3,
    )
    # Use a fixed seed for the reset within this fixture
    gs = GameState(config=test_config, initial_seed=456)
    # gs.reset() # reset is called in __init__

    # Manually set the shapes we want for the test
    shape1 = Shape([(0, 0, False)], color=DEFAULT_TEST_COLOR)  # Down
    shape2 = Shape([(0, 0, True)], color=DEFAULT_TEST_COLOR)  # Up
    shape3 = Shape(
        [(0, 0, False), (1, 0, False)], color=DEFAULT_TEST_COLOR
    )  # Two downs (vertical)

    gs.shapes = [
        copy.deepcopy(shape1),
        copy.deepcopy(shape2),
        copy.deepcopy(shape3),
    ]
    # Force recalculation of valid actions after manually setting shapes
    gs.valid_actions(force_recalculate=True)
    return gs


def test_game_state_initialization(default_game_state: GameState):
    """Test basic initialization of GameState."""
    gs = default_game_state
    assert gs.env_config is not None
    assert gs.grid_data is not None
    assert len(gs.shapes) == gs.env_config.NUM_SHAPE_SLOTS
    assert gs.game_score() == 0
    assert gs._game_over_reason is None or "No valid actions" in gs._game_over_reason
    assert len(gs.valid_actions()) > 0 or gs.is_over()


def test_game_state_reset(default_game_state: GameState):
    """Test resetting the GameState."""
    gs = default_game_state
    initial_shapes_before_step = copy.deepcopy(gs.shapes)
    action = next(iter(gs.valid_actions()), None)

    if action is not None:
        gs.step(action)
        assert gs.game_score() > 0 or len(gs.valid_actions()) == 0
    else:
        pass

    gs.reset()

    assert gs.game_score() == 0
    assert gs._game_over_reason is None or "No valid actions" in gs._game_over_reason
    assert gs.grid_data.is_empty()
    assert len(gs.shapes) == gs.env_config.NUM_SHAPE_SLOTS
    assert all(s is not None for s in gs.shapes)
    assert gs.shapes != initial_shapes_before_step
    assert len(gs.valid_actions()) > 0 or gs.is_over()


def test_game_state_step(default_game_state: GameState):
    """Test a single valid step."""
    gs = default_game_state
    initial_score = gs.game_score()
    initial_shapes = [s.copy() if s else None for s in gs.shapes]
    initial_shape_count = sum(1 for s in initial_shapes if s is not None)

    if not gs.valid_actions():
        pytest.skip("Cannot perform step test: no valid actions initially.")

    action = next(iter(gs.valid_actions()))
    shape_index, r, c = decode_action(action, gs.env_config)
    shape_placed = gs.shapes[shape_index]
    assert shape_placed is not None, "Action corresponds to an empty shape slot."
    placed_triangle_count = len(shape_placed.triangles)

    logging.debug(
        f"Before step: Action={action}, ShapeIdx={shape_index}, Pos=({r},{c})"
    )
    logging.debug(f"Before step: Score={initial_score}, Shapes={gs.shapes}")
    logging.debug(f"Before step: Valid Actions Count={len(gs.valid_actions())}")

    reward, done = gs.step(action)

    logging.debug(f"After step: Reward={reward}, Done={done}")
    logging.debug(f"After step: Score={gs.game_score()}, Shapes={gs.shapes}")
    logging.debug(f"After step: Valid Actions Count={len(gs.valid_actions())}")
    logging.debug(f"After step: Grid Occupied Sum={np.sum(gs.grid_data._occupied_np)}")

    assert not done or gs.is_over()
    assert reward is not None
    assert gs.shapes[shape_index] is None

    if placed_triangle_count > 0:
        assert not gs.grid_data.is_empty(), (
            "Grid is empty after placing a shape with triangles"
        )
    else:
        pass

    current_shape_count = sum(1 for s in gs.shapes if s is not None)
    if initial_shape_count == 1:
        assert current_shape_count == gs.env_config.NUM_SHAPE_SLOTS
    else:
        expected_count = initial_shape_count - 1
        assert current_shape_count == expected_count

    assert isinstance(gs.valid_actions(), set)


def test_game_state_step_invalid_action(default_game_state: GameState):
    """Test stepping with an invalid action index."""
    gs = default_game_state
    invalid_action = ActionType(-1)
    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action)

    invalid_action_large = ActionType(gs.env_config.ACTION_DIM)
    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action_large)

    empty_slot_idx = -1
    for i, shape in enumerate(gs.shapes):
        if shape is None:
            empty_slot_idx = i
            break
    if empty_slot_idx != -1:
        r, c = 0, 0
        found = False
        for r_try in range(gs.env_config.ROWS):
            start_c, end_c = gs.env_config.PLAYABLE_RANGE_PER_ROW[r_try]
            for c_try in range(start_c, end_c):
                r, c = r_try, c_try
                found = True
                break
            if found:
                break
        if not found:
            pytest.skip("Cannot find playable cell for empty slot test.")

        action_for_empty_slot = encode_action(empty_slot_idx, r, c, gs.env_config)
        assert action_for_empty_slot not in gs.valid_actions()
        with pytest.raises(
            ValueError, match="Action is not in the set of valid actions"
        ):
            gs.step(action_for_empty_slot)


def test_game_state_step_invalid_placement(default_game_state: GameState):
    """Test stepping with an action that is geometrically invalid."""
    gs = default_game_state

    if not gs.valid_actions():
        pytest.skip("No valid actions available to perform the first step.")

    action1 = next(iter(gs.valid_actions()))
    shape_index1, r1, c1 = decode_action(action1, gs.env_config)
    gs.step(action1)

    available_shape_idx = -1
    for idx, shape in enumerate(gs.shapes):
        if shape is not None:
            available_shape_idx = idx
            break

    if available_shape_idx == -1:
        if all(s is None for s in gs.shapes):
            pytest.skip("All shapes used, refill likely occurred or game ended.")
        else:
            pytest.skip("No shapes left after first step.")

    invalid_action = encode_action(available_shape_idx, r1, c1, gs.env_config)

    if invalid_action in gs.valid_actions():
        logging.warning(
            f"DEBUG: Action {invalid_action} (shape {available_shape_idx} at {r1},{c1}) is unexpectedly in valid_actions()"
        )
        pytest.skip(
            "Test setup failed: Action for invalid placement is in valid_actions()."
        )

    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action)


def test_game_state_is_over(default_game_state: GameState, mocker: MockerFixture):
    """Test the is_over condition by mocking valid_actions."""
    gs = default_game_state
    gs.is_over()
    gs.get_outcome()

    mocker.patch.object(
        gs, "valid_actions", return_value=set(), autospec=True
    )
    gs._game_over_reason = "Forced by mock"
    gs._game_over = True

    assert gs.is_over()
    assert gs.get_outcome() == -1.0
    assert "Forced by mock" in gs.get_game_over_reason()

    mocker.stopall()
    gs.reset()

    final_is_over = gs.is_over()
    final_outcome = gs.get_outcome()

    if final_is_over:
        assert final_outcome == -1.0
        assert "No valid actions available at start" in gs.get_game_over_reason()
        logging.info("Note: Game is over immediately after reset (no valid actions).")
    else:
        assert final_outcome == 0.0
        assert gs.get_game_over_reason() is None


def test_game_state_copy(default_game_state: GameState):
    """Test the copy method of GameState."""
    gs1 = default_game_state
    action1 = next(iter(gs1.valid_actions()), None)

    if action1:
        gs1.step(action1)

    gs2 = gs1.copy()

    assert gs1.game_score() == gs2.game_score()
    assert gs1.env_config == gs2.env_config
    assert gs1._game_over_reason == gs2._game_over_reason
    assert gs1.is_over() == gs2.is_over()

    assert gs1.grid_data is not gs2.grid_data
    assert np.array_equal(gs1.grid_data._occupied_np, gs2.grid_data._occupied_np)
    assert np.array_equal(gs1.grid_data._color_id_np, gs2.grid_data._color_id_np)
    assert np.array_equal(gs1.grid_data._death_np, gs2.grid_data._death_np)
    assert gs1.grid_data._occupied_np is not gs2.grid_data._occupied_np
    assert gs1.grid_data._color_id_np is not gs2.grid_data._color_id_np
    assert gs1.grid_data._death_np is not gs2.grid_data._death_np

    assert gs1.shapes is not gs2.shapes
    assert len(gs1.shapes) == len(gs2.shapes)
    for i in range(len(gs1.shapes)):
        if gs1.shapes[i] is None:
            assert gs2.shapes[i] is None
        else:
            assert gs1.shapes[i] == gs2.shapes[i]
            assert gs1.shapes[i] is not gs2.shapes[i]

    assert gs1.valid_actions() == gs2.valid_actions()
    if (
        hasattr(gs1, "_valid_actions_cache")
        and gs1._valid_actions_cache is not None
        and gs2._valid_actions_cache is not None
    ):
        assert gs1._valid_actions_cache is not gs2._valid_actions_cache

    action2 = next(iter(gs2.valid_actions()), None)
    if not action2:
        assert not gs1.valid_actions()
        return

    logging.debug(f"gs2 Before step: Action={action2}")
    logging.debug(f"gs2 Before step: Score={gs2.game_score()}, Shapes={gs2.shapes}")
    logging.debug(f"gs2 Before step: Valid Actions Count={len(gs2.valid_actions())}")
    logging.debug(
        f"gs2 Before step: Grid Occupied Sum={np.sum(gs2.grid_data._occupied_np)}"
    )

    reward2, done2 = gs2.step(action2)

    logging.debug(f"gs2 After step: Reward={reward2}, Done={done2}")
    logging.debug(f"gs2 After step: Score={gs2.game_score()}, Shapes={gs2.shapes}")
    logging.debug(f"gs2 After step: Valid Actions Count={len(gs2.valid_actions())}")
    logging.debug(
        f"gs2 After step: Grid Occupied Sum={np.sum(gs2.grid_data._occupied_np)}"
    )
    logging.debug(
        f"gs1 After gs2 step: Grid Occupied Sum={np.sum(gs1.grid_data._occupied_np)}"
    )

    assert gs1.game_score() != gs2.game_score() or reward2 == 0.0

    shape_idx2, _, _ = decode_action(action2, gs2.env_config)
    assert gs2.shapes[shape_idx2] is None

    assert not np.array_equal(gs1.grid_data._occupied_np, gs2.grid_data._occupied_np), (
        "Grid occupied state should differ after step in copy"
    )


def test_game_state_get_outcome_non_terminal(default_game_state: GameState):
    """Test get_outcome when the game is not over."""
    gs = default_game_state
    if gs.is_over():
        pytest.skip("Game is over initially, cannot test non-terminal outcome.")
    assert not gs.is_over()
    assert gs.get_outcome() == 0.0


def test_game_state_step_triggers_game_over(
    game_state_with_fixed_shapes: GameState, mocker: MockerFixture
):
    """Test that placing the last possible piece triggers game over."""
    gs = game_state_with_fixed_shapes  # Uses 3x3 grid

    # Setup: Fill grid except for two specific *playable* cells
    # (1,0) is Down, (1,1) is Up
    gs.grid_data._occupied_np[:, :] = True
    gs.grid_data._occupied_np[1, 0] = False  # Make (1,0) empty
    gs.grid_data._occupied_np[1, 1] = False  # Make (1,1) empty
    gs.grid_data._color_id_np[:, :] = 0
    gs.grid_data._color_id_np[1, 0] = -1
    gs.grid_data._color_id_np[1, 1] = -1

    # Setup: Ensure only the first two shapes are available
    # Shape 0: Single Down. Shape 1: Single Up.
    gs.shapes[2] = None
    gs.valid_actions(force_recalculate=True)  # Recalculate valid actions

    # Verify shape 0 (Down) can be placed at (1,0) [Down]
    assert gs.shapes[0] is not None
    assert GridLogic.can_place(gs.grid_data, gs.shapes[0], 1, 0), (
        "Shape 0 (Down) should be placeable at (1,0)"
    )
    action1 = encode_action(0, 1, 0, gs.env_config)
    assert action1 in gs.valid_actions()

    # Verify shape 1 (Up) can be placed at (1,1) [Up]
    assert gs.shapes[1] is not None
    assert GridLogic.can_place(gs.grid_data, gs.shapes[1], 1, 1), (
        "Shape 1 (Up) should be placeable at (1,1)"
    )
    action2 = encode_action(1, 1, 1, gs.env_config)
    assert action2 in gs.valid_actions()

    mock_refill = mocker.patch(
        "trianglengin.core.environment.shapes.logic.refill_shape_slots"
    )

    # Step 1: Place shape 0 at (1,0)
    reward1, done1 = gs.step(action1)
    assert not done1, "Game should not be over after first placement"
    assert gs.shapes[0] is None
    assert gs.shapes[1] is not None  # Shape 1 still available
    assert gs.shapes[2] is None
    mock_refill.assert_not_called()
    assert gs.grid_data._occupied_np[1, 0]  # Verify placement

    # Step 2: Place shape 1 at (1,1) (the last available shape)
    reward2, done2 = gs.step(action2)

    mock_refill.assert_not_called()  # Refill shouldn't happen
    assert done2, "The second step (placing last shape) should have returned done=True"
    assert gs.is_over(), "Game state should be marked as over after placing last shape"
    assert "No valid actions available" in gs.get_game_over_reason()
    assert gs.get_outcome() == -1.0

    # Final state check
    assert gs.shapes[0] is None
    assert gs.shapes[1] is None
    assert gs.shapes[2] is None
    assert gs.grid_data._occupied_np[1, 0]
    assert gs.grid_data._occupied_np[1, 1]
    playable_mask = ~gs.grid_data._death_np
    assert gs.grid_data._occupied_np[playable_mask].all()


def test_game_state_forced_game_over(default_game_state: GameState):
    """Test forcing game over manually."""
    gs = default_game_state
    if gs.is_over():
        pytest.skip("Game is over initially, cannot test forcing.")

    assert not gs.is_over()
    gs.force_game_over("Test reason")
    assert gs.is_over()
    assert "Test reason" in gs.get_game_over_reason()
    assert gs.get_outcome() == -1.0
