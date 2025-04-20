import logging
import random
from typing import TYPE_CHECKING  # Added Set, Tuple

from trianglengin.core.environment import shapes as ShapeLogic
from trianglengin.core.environment.grid import logic as GridLogic
from trianglengin.core.structs.constants import COLOR_TO_ID_MAP, NO_COLOR_ID

if TYPE_CHECKING:
    from trianglengin.config import EnvConfig
    from trianglengin.core.environment.game_state import GameState
    from trianglengin.core.environment.grid.line_cache import Coord  # Import Coord


logger = logging.getLogger(__name__)


def calculate_reward(
    placed_count: int,
    cleared_count: int,  # Expect int, not set
    is_game_over: bool,
    config: "EnvConfig",
) -> float:
    """
    Calculates the step reward based on the new specification (v3).

    Args:
        placed_count: Number of triangles successfully placed.
        cleared_count: Number of unique triangles cleared this step.
        is_game_over: Boolean indicating if the game ended *after* this step.
        config: Environment configuration containing reward constants.

    Returns:
        The calculated step reward.
    """
    reward = 0.0

    # 1. Placement Reward
    reward += placed_count * config.REWARD_PER_PLACED_TRIANGLE

    # 2. Line Clear Reward
    reward += cleared_count * config.REWARD_PER_CLEARED_TRIANGLE

    # 3. Survival Reward OR Game Over Penalty
    if is_game_over:
        # Apply penalty only if game ended THIS step
        reward += config.PENALTY_GAME_OVER
    else:
        reward += config.REWARD_PER_STEP_ALIVE

    logger.debug(
        f"Calculated Reward: Placement({placed_count * config.REWARD_PER_PLACED_TRIANGLE:.3f}) "
        f"+ LineClear({cleared_count * config.REWARD_PER_CLEARED_TRIANGLE:.3f}) "
        f"+ {'GameOver' if is_game_over else 'Survival'}({config.PENALTY_GAME_OVER if is_game_over else config.REWARD_PER_STEP_ALIVE:.3f}) "
        f"= {reward:.3f}"
    )
    return reward


def execute_placement(
    game_state: "GameState", shape_idx: int, r: int, c: int, rng: random.Random
) -> tuple[float, int, int]:
    """
    Places a shape, clears lines, updates game state, triggers refill, and calculates reward.

    Args:
        game_state: The current game state (will be modified).
        shape_idx: Index of the shape to place.
        r: Target row for placement.
        c: Target column for placement.
        rng: Random number generator for shape refilling.

    Returns:
        Tuple[float, int, int]: (step_reward, cleared_triangle_count, placed_triangle_count)
    """
    shape = game_state.shapes[shape_idx]
    if not shape:
        logger.error(f"Attempted to place an empty shape slot: {shape_idx}")
        # Return zero reward and counts if shape is missing
        return 0.0, 0, 0

    # Check placement validity using GridLogic
    if not GridLogic.can_place(game_state.grid_data, shape, r, c):
        # This case should ideally be prevented by GameState.step checking valid_actions first.
        # Log an error if reached.
        logger.error(
            f"Invalid placement attempted in execute_placement: Shape {shape_idx} at ({r},{c}). "
            "This should have been caught earlier by checking valid_actions."
        )
        # Return zero reward and counts for invalid placement attempt.
        return 0.0, 0, 0

    # --- Place the shape ---
    placed_coords: set[Coord] = set()  # Use Coord type alias
    placed_count = 0
    color_id = COLOR_TO_ID_MAP.get(shape.color, NO_COLOR_ID)
    if color_id == NO_COLOR_ID:
        logger.warning(
            f"Shape color {shape.color} not found in COLOR_TO_ID_MAP! Using ID 0."
        )
        color_id = 0  # Assign a default ID

    for dr, dc, _ in shape.triangles:
        tri_r, tri_c = r + dr, c + dc
        # Assume valid coordinates as can_place passed
        if game_state.grid_data.valid(tri_r, tri_c):  # Double check bounds just in case
            if (
                not game_state.grid_data._death_np[tri_r, tri_c]
                and not game_state.grid_data._occupied_np[tri_r, tri_c]
            ):
                game_state.grid_data._occupied_np[tri_r, tri_c] = True
                game_state.grid_data._color_id_np[tri_r, tri_c] = color_id
                placed_coords.add((tri_r, tri_c))
                placed_count += 1
            else:
                # This case should not happen if can_place was checked correctly
                logger.error(
                    f"Placement conflict at ({tri_r},{tri_c}) during execution despite passing can_place."
                )
        else:
            # This case should not happen if can_place was checked correctly
            logger.error(
                f"Invalid coordinates ({tri_r},{tri_c}) during placement execution despite passing can_place."
            )

    game_state.shapes[shape_idx] = None  # Remove shape from slot
    # Update internal step stats (if they exist)
    if hasattr(game_state, "pieces_placed_this_step"):
        game_state.pieces_placed_this_step = placed_count

    # --- Check and clear lines ---
    lines_cleared_count, unique_coords_cleared, _ = GridLogic.check_and_clear_lines(
        game_state.grid_data, placed_coords
    )
    cleared_count = len(unique_coords_cleared)
    # Update internal step stats (if they exist)
    if hasattr(game_state, "triangles_cleared_this_step"):
        game_state.triangles_cleared_this_step = cleared_count

    # --- Update Score (Using internal attribute) ---
    # Simple scoring: +1 per piece placed, +2 per triangle cleared
    # Reward calculation below is separate and configurable
    game_state._game_score += placed_count + cleared_count * 2  # Assign to _game_score

    # --- Refill shapes if all slots are empty ---
    if all(s is None for s in game_state.shapes):
        logger.debug("All shape slots empty, triggering batch refill.")
        ShapeLogic.refill_shape_slots(game_state, rng)
        # Note: Refilling might immediately make the game non-over if it was previously
        # Game over check needs to happen *after* potential refill

    # --- Determine if game is over AFTER placement and refill ---
    # We don't set game_state._game_over here directly.
    # GameState.step will call valid_actions() after this function returns
    # to determine the final game over status for the step.
    # Force recalculation to see if game *would* end without further steps
    is_game_over_after_step = not game_state.valid_actions(force_recalculate=True)

    # --- Calculate Reward based on the outcome of this step ---
    step_reward = calculate_reward(
        placed_count=placed_count,
        cleared_count=cleared_count,  # Pass the count
        is_game_over=is_game_over_after_step,  # Pass the potential end state
        config=game_state.env_config,
    )

    # Return reward and stats for this step
    return step_reward, cleared_count, placed_count
