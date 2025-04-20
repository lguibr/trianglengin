# File: tests/core/environment/test_game_state.py
import logging

import numpy as np
import pytest
from pytest_mock import MockerFixture

import trianglengin.core.environment.grid.logic as GridLogic
from trianglengin.config.env_config import EnvConfig

# Import shapes module
from trianglengin.core.environment import shapes as ShapeLogic
from trianglengin.core.environment.action_codec import (
    ActionType,
    decode_action,
    encode_action,
)
from trianglengin.core.environment.game_state import GameState
from trianglengin.core.structs.shape import Shape
from trianglengin.visualization.core.colors import Color

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

# Define a default color for shapes in tests
DEFAULT_TEST_COLOR: Color = (100, 100, 100)


@pytest.fixture
def default_config() -> EnvConfig:
    """Fixture for default environment configuration."""
    return EnvConfig()


@pytest.fixture
def default_game_state(default_config: EnvConfig) -> GameState:
    """Fixture for a default GameState."""
    return GameState(config=default_config, initial_seed=123)


@pytest.fixture
def game_state_with_fixed_shapes() -> GameState:
    """Fixture for a GameState with predictable shapes for testing."""
    test_config = EnvConfig(
        ROWS=3,
        COLS=3,
        PLAYABLE_RANGE_PER_ROW=[(0, 3), (0, 3), (0, 3)],
        NUM_SHAPE_SLOTS=3,
    )
    gs = GameState(config=test_config, initial_seed=456)
    shape1 = Shape([(0, 0, False)], color=DEFAULT_TEST_COLOR)
    shape2 = Shape([(0, 0, True)], color=DEFAULT_TEST_COLOR)
    shape3 = Shape([(0, 0, False), (1, 0, False)], color=DEFAULT_TEST_COLOR)
    gs.shapes = [shape1.copy(), shape2.copy(), shape3.copy()]
    gs.valid_actions(force_recalculate=True)
    return gs


def test_game_state_initialization(default_game_state: GameState):
    """Test basic initialization of GameState."""
    gs = default_game_state
    assert gs.env_config is not None
    assert gs.grid_data is not None
    assert len(gs.shapes) == gs.env_config.NUM_SHAPE_SLOTS
    assert gs.game_score() == 0
    is_initially_over = gs.is_over()  # Check if game over
    if is_initially_over:
        assert "No valid actions available at start" in gs.get_game_over_reason()
    else:
        assert gs.get_game_over_reason() is None
        assert len(gs.valid_actions()) > 0


def test_game_state_reset(default_game_state: GameState):
    """Test resetting the GameState."""
    gs = default_game_state
    initial_shapes_before_step = [s.copy() if s else None for s in gs.shapes]
    action = next(iter(gs.valid_actions()), None)

    if action is not None:
        gs.step(action)
        assert gs.game_score() > 0 or not gs.valid_actions()
    else:
        pass

    gs.reset()

    assert gs.game_score() == 0
    is_over_after_reset = gs.is_over()
    if is_over_after_reset:
        assert "No valid actions available at start" in gs.get_game_over_reason()
    else:
        assert gs.get_game_over_reason() is None

    assert gs.grid_data.is_empty()
    assert len(gs.shapes) == gs.env_config.NUM_SHAPE_SLOTS
    assert all(s is not None for s in gs.shapes)

    shapes_after_reset = [s.copy() if s else None for s in gs.shapes]
    if action is not None:
        assert [s.triangles for s in shapes_after_reset if s] != [
            s.triangles for s in initial_shapes_before_step if s
        ] or [s.color for s in shapes_after_reset if s] != [
            s.color for s in initial_shapes_before_step if s
        ]

    if not is_over_after_reset:
        assert len(gs.valid_actions()) > 0


def test_game_state_step(default_game_state: GameState):
    """Test a single valid step."""
    gs = default_game_state
    initial_score = gs.game_score()
    initial_shapes = [s.copy() if s else None for s in gs.shapes]
    initial_shape_count = sum(1 for s in initial_shapes if s is not None)

    valid_actions = gs.valid_actions()
    if not valid_actions:
        pytest.skip("Cannot perform step test: no valid actions initially.")

    action = next(iter(valid_actions))
    shape_index, r, c = decode_action(action, gs.env_config)
    shape_placed = gs.shapes[shape_index]
    assert shape_placed is not None, "Action corresponds to an empty shape slot."
    placed_triangle_count = len(shape_placed.triangles)

    logging.debug(
        f"Before step: Action={action}, ShapeIdx={shape_index}, Pos=({r},{c})"
    )
    logging.debug(f"Before step: Score={initial_score}, Shapes={gs.shapes}")
    logging.debug(f"Before step: Valid Actions Count={len(valid_actions)}")

    reward, done = gs.step(action)

    logging.debug(f"After step: Reward={reward}, Done={done}")
    logging.debug(f"After step: Score={gs.game_score()}, Shapes={gs.shapes}")
    logging.debug(f"After step: Valid Actions Count={len(gs.valid_actions())}")
    logging.debug(f"After step: Grid Occupied Sum={np.sum(gs.grid_data._occupied_np)}")

    assert done == gs.is_over()
    assert reward is not None
    assert gs.shapes[shape_index] is None

    if placed_triangle_count > 0:
        playable_mask = ~gs.grid_data._death_np
        if not gs.grid_data._occupied_np[playable_mask].any():
            logging.warning(
                "Grid became empty after placing a shape (likely full clear)."
            )
        assert gs.grid_data._occupied_np.any(), (
            "Grid occupied status unexpected after placement."
        )
    else:
        pass

    current_shape_count = sum(1 for s in gs.shapes if s is not None)
    if initial_shape_count == 1:
        assert current_shape_count == gs.env_config.NUM_SHAPE_SLOTS
    elif initial_shape_count > 1:
        expected_count = initial_shape_count - 1
        assert current_shape_count == expected_count

    assert isinstance(gs.valid_actions(), set)


def test_game_state_step_invalid_action(default_game_state: GameState):
    """Test stepping with an invalid action index."""
    gs = default_game_state
    invalid_action = ActionType(-1)
    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action)

    invalid_action_large = ActionType(int(gs.env_config.ACTION_DIM))
    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action_large)

    empty_slot_idx = -1
    for i, shape in enumerate(gs.shapes):
        if shape is None:
            empty_slot_idx = i
            break

    if empty_slot_idx != -1:
        r, c = 0, 0
        found_playable = False
        for r_try in range(gs.env_config.ROWS):
            start_c, end_c = gs.env_config.PLAYABLE_RANGE_PER_ROW[r_try]
            if start_c < end_c:
                r, c = r_try, start_c
                found_playable = True
                break
        if not found_playable:
            pytest.skip("Cannot find any playable cell for empty slot test.")

        action_for_empty_slot = encode_action(empty_slot_idx, r, c, gs.env_config)
        assert action_for_empty_slot not in gs.valid_actions()
        with pytest.raises(
            ValueError, match="Action is not in the set of valid actions"
        ):
            gs.step(action_for_empty_slot)


def test_game_state_step_invalid_placement(default_game_state: GameState):
    """Test stepping with an action that is geometrically invalid."""
    gs = default_game_state

    valid_actions_initial = gs.valid_actions()
    if not valid_actions_initial:
        pytest.skip("No valid actions available to perform the first step.")

    action1 = next(iter(valid_actions_initial))
    shape_index1, r1, c1 = decode_action(action1, gs.env_config)
    reward1, done1 = gs.step(action1)

    if done1:
        pytest.skip("Game ended after the first step, cannot test invalid placement.")

    available_shape_idx = -1
    for idx, shape in enumerate(gs.shapes):
        if shape is not None:
            available_shape_idx = idx
            break

    if available_shape_idx == -1:
        pytest.skip(
            "No shapes left available after first step (refill occurred?), cannot test invalid placement."
        )

    invalid_action = encode_action(available_shape_idx, r1, c1, gs.env_config)

    current_valid_actions = gs.valid_actions()
    if invalid_action in current_valid_actions:
        logging.warning(
            f"DEBUG: Grid occupied at ({r1},{c1}): {gs.grid_data.is_occupied(r1, c1)}"
        )
        pytest.skip(
            "Test setup failed: Action for invalid placement is unexpectedly valid."
        )

    with pytest.raises(ValueError, match="Action is not in the set of valid actions"):
        gs.step(invalid_action)


def test_game_state_is_over(default_game_state: GameState, mocker: MockerFixture):
    """Test the is_over condition by mocking valid_actions."""
    gs = default_game_state

    initial_is_over = gs.is_over()
    initial_outcome = gs.get_outcome()
    if initial_is_over:
        assert initial_outcome == -1.0
        assert "No valid actions available at start" in gs.get_game_over_reason()
    else:
        assert initial_outcome == 0.0
        assert gs.get_game_over_reason() is None

    mocker.patch.object(gs, "valid_actions", return_value=set(), autospec=True)
    gs._game_over = True
    gs._game_over_reason = "Forced by mock"

    assert gs.is_over()
    assert gs.get_outcome() == -1.0
    assert "Forced by mock" in gs.get_game_over_reason()

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
    assert gs1.is_over() == gs2.is_over()
    assert gs1.get_game_over_reason() == gs2.get_game_over_reason()
    assert gs1.current_step == gs2.current_step

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
            assert gs1.shapes[i] is not None
            assert gs2.shapes[i] is not None
            assert gs1.shapes[i] == gs2.shapes[i]
            assert gs1.shapes[i] is not gs2.shapes[i]

    gs1_cache = gs1.valid_actions()
    gs2_cache = gs2.valid_actions()
    assert gs1_cache == gs2_cache
    if gs1._valid_actions_cache is not None and gs2._valid_actions_cache is not None:
        assert gs1._valid_actions_cache is not gs2._valid_actions_cache

    action2 = next(iter(gs2.valid_actions()), None)
    if not action2:
        assert not gs1.valid_actions()
        return

    reward2, done2 = gs2.step(action2)
    score1_after_gs2_step = gs1.game_score()
    grid1_occupied_after_gs2_step = gs1.grid_data._occupied_np.copy()
    shapes1_after_gs2_step = [s.copy() if s else None for s in gs1.shapes]

    assert score1_after_gs2_step != gs2.game_score() or reward2 == 0.0
    assert np.array_equal(grid1_occupied_after_gs2_step, gs1.grid_data._occupied_np)
    assert not np.array_equal(gs1.grid_data._occupied_np, gs2.grid_data._occupied_np)
    assert shapes1_after_gs2_step == gs1.shapes


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
    """Test that placing the last available shape triggers refill, preventing immediate game over."""
    gs = game_state_with_fixed_shapes  # Uses 3x3 grid fixture

    empty_r_down, empty_c_down = 0, 0
    empty_r_up, empty_c_up = 0, 1

    # Setup: Fill all EXCEPT (0,0) and (0,1). (0,2) remains filled.
    playable_mask = ~gs.grid_data._death_np
    gs.grid_data._occupied_np[playable_mask] = True
    gs.grid_data._color_id_np[playable_mask] = 0
    gs.grid_data._occupied_np[empty_r_down, empty_c_down] = False
    gs.grid_data._occupied_np[empty_r_up, empty_c_up] = False
    gs.grid_data._color_id_np[empty_r_down, empty_c_down] = -1
    gs.grid_data._color_id_np[empty_r_up, empty_c_up] = -1
    # Ensure (0,2) is occupied to test line clear
    gs.grid_data._occupied_np[0, 2] = True
    gs.grid_data._color_id_np[0, 2] = 0

    # Start with shapes 0 (Down) and 1 (Up), slot 2 is None
    gs.shapes[2] = None
    # --- MOVED Action Calculation AFTER final grid setup ---
    gs.valid_actions(force_recalculate=True)  # Re-validate actions with corrected setup

    # Verify actions are valid *after* the final setup
    assert gs.shapes[0] is not None and gs.shapes[0].triangles == [(0, 0, False)]
    action1 = encode_action(0, empty_r_down, empty_c_down, gs.env_config)
    assert GridLogic.can_place(gs.grid_data, gs.shapes[0], empty_r_down, empty_c_down)
    assert action1 in gs.valid_actions()

    assert gs.shapes[1] is not None and gs.shapes[1].triangles == [(0, 0, True)]
    action2 = encode_action(1, empty_r_up, empty_c_up, gs.env_config)
    assert GridLogic.can_place(gs.grid_data, gs.shapes[1], empty_r_up, empty_c_up)
    assert action2 in gs.valid_actions()
    # --- END MOVED Action Calculation ---

    # Mock refill logic to verify it's called
    mock_refill = mocker.patch(
        "trianglengin.core.environment.shapes.logic.refill_shape_slots",
        wraps=ShapeLogic.refill_shape_slots,  # Use wraps to still execute the original logic
    )

    # --- Step 1: Place shape 0 at (0,0) ---
    reward1, done1 = gs.step(action1)  # Use action1 calculated after setup
    assert not done1, "Game should not be over after first placement (corrected setup)"
    assert gs.grid_data._occupied_np[empty_r_down, empty_c_down]
    mock_refill.assert_not_called()
    assert gs.shapes[0] is None
    assert gs.shapes[1] is not None  # Shape 1 should still be there
    assert gs.shapes[2] is None

    # --- Step 2: Place shape 1 at (0,1) ---
    # This completes the horizontal line (0,0), (0,1), (0,2)
    # It also makes all slots empty, triggering refill.
    reward2, done2 = gs.step(action2)  # Use action2 calculated after setup

    # Assertions after the second step (with line clear and refill):
    mock_refill.assert_called_once()  # Refill called because slots became empty
    assert not done2, "Game should NOT be over because refill provides new actions"
    assert not gs.is_over(), "Game state should NOT be marked as over after refill"
    assert gs.get_outcome() == 0.0
    assert len(gs.valid_actions()) > 0

    # Check that the line was actually cleared
    assert not gs.grid_data._occupied_np[0, 0], "(0,0) should be cleared"
    assert not gs.grid_data._occupied_np[0, 1], "(0,1) should be cleared"
    assert not gs.grid_data._occupied_np[0, 2], "(0,2) should be cleared"

    # Check shapes are refilled
    assert gs.shapes[0] is not None
    assert gs.shapes[1] is not None
    assert gs.shapes[2] is not None


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
    assert not gs.valid_actions()
