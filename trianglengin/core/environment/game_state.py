# trianglengin/core/environment/game_state.py
import copy
import logging
import random
from typing import TYPE_CHECKING

from trianglengin.config.env_config import EnvConfig
from trianglengin.core.environment.action_codec import (
    ActionType,
    decode_action,
)
from trianglengin.core.environment.grid.grid_data import GridData
from trianglengin.core.environment.logic.actions import get_valid_actions
from trianglengin.core.environment.logic.step import execute_placement
from trianglengin.core.environment.shapes import logic as ShapeLogic

if TYPE_CHECKING:
    from trianglengin.core.structs.shape import Shape  # Corrected import path


log = logging.getLogger(__name__)


class GameState:
    """
    Represents the mutable state of the game environment.
    """

    def __init__(
        self, config: EnvConfig | None = None, initial_seed: int | None = None
    ):
        self.env_config: EnvConfig = config if config else EnvConfig()
        self._rng = random.Random(initial_seed)
        self.grid_data: GridData = GridData(self.env_config)
        self.shapes: list[Shape | None] = [None] * self.env_config.NUM_SHAPE_SLOTS
        self._game_score: float = 0.0
        self._game_over: bool = False
        self._game_over_reason: str | None = None
        self.current_step: int = 0
        self._valid_actions_cache: set[ActionType] | None = None
        self.triangles_cleared_this_step: int = 0
        self.pieces_placed_this_step: int = 0
        self.reset()

    def reset(self) -> None:
        """Resets the game to an initial state."""
        self.grid_data.reset()
        self.shapes = [None] * self.env_config.NUM_SHAPE_SLOTS
        self._game_score = 0.0
        self._game_over = False
        self._game_over_reason = None
        self.current_step = 0
        self.triangles_cleared_this_step = 0
        self.pieces_placed_this_step = 0
        self._valid_actions_cache = None
        ShapeLogic.refill_shape_slots(self, self._rng)
        _ = self.valid_actions()
        if not self._valid_actions_cache:
            self._game_over = True
            self._game_over_reason = "No valid actions available at start."
            log.warning(self._game_over_reason)

    def step(self, action_index: ActionType) -> tuple[float, bool]:
        """
        Performs one game step based on the chosen action.
        Returns: (reward, done)
        Raises: ValueError if action is invalid.
        """
        if self.is_over():
            log.warning("Attempted to step in a game that is already over.")
            return 0.0, True

        if action_index not in self.valid_actions():
            log.error(
                f"Invalid action {action_index} provided. Valid: {self.valid_actions()}"
            )
            raise ValueError("Action is not in the set of valid actions")

        shape_idx, r, c = decode_action(action_index, self.env_config)

        # --- Execute Placement ---
        reward: float
        cleared_count: int
        placed_count: int
        # Add missing self._rng argument
        reward, cleared_count, placed_count = execute_placement(
            self, shape_idx, r, c, self._rng
        )
        # --- End Execute Placement ---

        self.current_step += 1
        self._valid_actions_cache = None  # Clear cache

        if not self.valid_actions():
            self._game_over = True
            self._game_over_reason = "No valid actions available."
            log.info(f"Game over at step {self.current_step}: {self._game_over_reason}")

        return reward, self._game_over

    def valid_actions(self, force_recalculate: bool = False) -> set[ActionType]:
        """
        Returns a set of valid encoded action indices for the current state.
        Uses a cache for performance unless force_recalculate is True.
        """
        if self._valid_actions_cache is None or force_recalculate:
            if self._game_over and not force_recalculate:
                # If game is over and not forcing, return empty set immediately
                # and ensure cache reflects this.
                self._valid_actions_cache = set()
                return self._valid_actions_cache
            else:
                # Calculate fresh valid actions
                current_valid_actions = get_valid_actions(self)
                # Only update cache if not forcing
                if not force_recalculate:
                    self._valid_actions_cache = current_valid_actions
                # Return the freshly calculated set
                return current_valid_actions

        # Return cached set if available and not forcing recalculation
        # Add type assertion for mypy if needed, though logic should ensure it's a set here
        # assert self._valid_actions_cache is not None
        return self._valid_actions_cache

    def is_over(self) -> bool:
        """Checks if the game is over."""
        if self._game_over:
            return True
        # Check valid_actions (which updates cache if None)
        if not self.valid_actions():
            self._game_over = True
            if not self._game_over_reason:
                self._game_over_reason = "No valid actions available."
            return True
        return False

    def get_outcome(self) -> float:
        """Returns terminal outcome: -1.0 for loss, 0.0 for ongoing."""
        return -1.0 if self.is_over() else 0.0

    def game_score(self) -> float:
        """Returns the current accumulated score."""
        return self._game_score

    def get_game_over_reason(self) -> str | None:
        """Returns the reason why the game ended, if it's over."""
        return self._game_over_reason

    def force_game_over(self, reason: str) -> None:
        """Forces the game to end immediately."""
        self._game_over = True
        self._game_over_reason = reason
        self._valid_actions_cache = set()
        log.warning(f"Game forced over: {reason}")

    def copy(self) -> "GameState":
        """Creates a deep copy for simulations (e.g., MCTS)."""
        new_state = GameState.__new__(GameState)
        memo = {id(self): new_state}
        new_state.env_config = self.env_config
        new_state._rng = random.Random()
        new_state._rng.setstate(self._rng.getstate())
        new_state.grid_data = copy.deepcopy(self.grid_data, memo)
        new_state.shapes = [s.copy() if s else None for s in self.shapes]
        new_state._game_score = self._game_score
        new_state._game_over = self._game_over
        new_state._game_over_reason = self._game_over_reason
        new_state.current_step = self.current_step
        new_state.triangles_cleared_this_step = self.triangles_cleared_this_step
        new_state.pieces_placed_this_step = self.pieces_placed_this_step
        new_state._valid_actions_cache = (
            self._valid_actions_cache.copy()
            if self._valid_actions_cache is not None
            else None
        )
        return new_state

    def __str__(self) -> str:
        shape_strs = [str(s.color) if s else "None" for s in self.shapes]
        status = "Over" if self.is_over() else "Ongoing"
        return (
            f"GameState(Step:{self.current_step}, Score:{self.game_score():.1f}, "
            f"Status:{status}, Shapes:[{', '.join(shape_strs)}])"
        )
