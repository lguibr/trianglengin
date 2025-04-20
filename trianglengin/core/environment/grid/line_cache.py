# File: trianglengin/core/environment/grid/line_cache.py
import logging
from typing import Final, Sequence, cast  # Added cast

from trianglengin.config.env_config import EnvConfig

log = logging.getLogger(__name__)

# Type aliases
Coord = tuple[int, int]
Line = tuple[Coord, ...]
LineFsSet = set[frozenset[Coord]]
CoordMap = dict[Coord, LineFsSet]
# Cache Key: Correct type hint for the tuple of tuples
ConfigKey = tuple[int, int, tuple[tuple[int, int], ...]]
CachedData = tuple[list[Line], CoordMap]
_LINE_CACHE: dict[ConfigKey, CachedData] = {}

# Directions
HORIZONTAL: Final = "h"
DIAGONAL_TL_BR: Final = "d1"
DIAGONAL_BL_TR: Final = "d2"


def _create_cache_key(config: EnvConfig) -> ConfigKey:
    """Creates an immutable cache key from relevant EnvConfig fields."""
    # Explicitly cast inner list elements to tuples and the result to the expected outer tuple type
    playable_ranges_tuple: tuple[tuple[int, int], ...] = cast(
        "tuple[tuple[int, int], ...]",
        tuple(tuple(item) for item in config.PLAYABLE_RANGE_PER_ROW),
    )
    return (
        config.ROWS,
        config.COLS,
        playable_ranges_tuple,
    )


def get_precomputed_lines_and_map(config: EnvConfig) -> CachedData:
    """
    Retrieves the precomputed maximal lines and the coordinate-to-lines map
    for a given configuration, using a cache. Computes if not found.
    """
    key = _create_cache_key(config)
    if key not in _LINE_CACHE:
        log.info(f"Cache miss for grid config: {key}. Computing maximal lines and map.")
        _LINE_CACHE[key] = _compute_maximal_lines_and_map(config)

    lines, coord_map = _LINE_CACHE[key]
    # Return copies
    return list(lines), {coord: set(lineset) for coord, lineset in coord_map.items()}


def _is_live(r: int, c: int, config: EnvConfig) -> bool:
    """Checks if a cell is within bounds and the playable range for its row."""
    if not (0 <= r < config.ROWS and 0 <= c < config.COLS):
        return False
    if r >= len(config.PLAYABLE_RANGE_PER_ROW):
        return False
    start_col, end_col = config.PLAYABLE_RANGE_PER_ROW[r]
    return start_col <= c < end_col


def _compute_maximal_lines_and_map(config: EnvConfig) -> CachedData:
    """
    Computes all *maximal* continuous lines of playable cells (horizontally and
    diagonally). Also builds the coordinate-to-lines map.
    A line must have at least length 1.
    """
    rows, cols = config.ROWS, config.COLS
    maximal_lines_set: set[Line] = set()
    visited_starts: set[tuple[Coord, str]] = set()

    for r_start in range(rows):
        for c_start in range(cols):
            if not _is_live(r_start, c_start, config):
                continue

            start_coord = (r_start, c_start)

            # --- Trace Horizontal ---
            if (start_coord, HORIZONTAL) not in visited_starts:
                line_h: list[Coord] = []
                cc_start_trace = c_start
                while _is_live(r_start, cc_start_trace - 1, config):
                    cc_start_trace -= 1
                trace_start_h = (r_start, cc_start_trace)

                cc_trace = trace_start_h[1]
                while _is_live(r_start, cc_trace, config):
                    coord = (r_start, cc_trace)
                    line_h.append(coord)
                    visited_starts.add((coord, HORIZONTAL))
                    cc_trace += 1
                if line_h:
                    maximal_lines_set.add(tuple(line_h))

            # --- Trace Diagonal TL-BR ---
            if (start_coord, DIAGONAL_TL_BR) not in visited_starts:
                line_d1: list[Coord] = []
                cr, cc = r_start, c_start
                while True:
                    is_up_prev = (cr + cc) % 2 != 0
                    prev_r, prev_c = (cr, cc - 1) if not is_up_prev else (cr - 1, cc)
                    if _is_live(prev_r, prev_c, config):
                        cr, cc = prev_r, prev_c
                    else:
                        break
                trace_start_d1 = (cr, cc)

                cr_trace, cc_trace = trace_start_d1
                while _is_live(cr_trace, cc_trace, config):
                    coord = (cr_trace, cc_trace)
                    line_d1.append(coord)
                    visited_starts.add((coord, DIAGONAL_TL_BR))
                    is_up = (cr_trace + cc_trace) % 2 != 0
                    next_r, next_c = (
                        (cr_trace + 1, cc_trace) if is_up else (cr_trace, cc_trace + 1)
                    )
                    cr_trace, cc_trace = next_r, next_c
                if line_d1:
                    maximal_lines_set.add(tuple(line_d1))

            # --- Trace Diagonal BL-TR ---
            if (start_coord, DIAGONAL_BL_TR) not in visited_starts:
                line_d2: list[Coord] = []
                cr, cc = r_start, c_start
                while True:
                    is_up_prev = (cr + cc) % 2 != 0
                    prev_r, prev_c = (cr, cc - 1) if is_up_prev else (cr + 1, cc)
                    if _is_live(prev_r, prev_c, config):
                        cr, cc = prev_r, prev_c
                    else:
                        break
                trace_start_d2 = (cr, cc)

                cr_trace, cc_trace = trace_start_d2
                while _is_live(cr_trace, cc_trace, config):
                    coord = (cr_trace, cc_trace)
                    line_d2.append(coord)
                    visited_starts.add((coord, DIAGONAL_BL_TR))
                    is_up = (cr_trace + cc_trace) % 2 != 0
                    next_r, next_c = (
                        (cr_trace - 1, cc_trace)
                        if not is_up
                        else (cr_trace, cc_trace + 1)
                    )
                    cr_trace, cc_trace = next_r, next_c
                if line_d2:
                    maximal_lines_set.add(tuple(line_d2))

    # --- Build Final List and Map ---
    final_lines_list = sorted(
        list(maximal_lines_set),
        key=lambda line: (line[0][0], line[0][1], len(line), line),
    )

    coord_map: CoordMap = {}
    for line_tuple in final_lines_list:
        line_fs = frozenset(line_tuple)
        for coord in line_tuple:
            if coord not in coord_map:
                coord_map[coord] = set()
            coord_map[coord].add(line_fs)

    key = _create_cache_key(config)
    log.info(
        f"Computed {len(final_lines_list)} unique maximal lines "
        f"and map for {len(coord_map)} coords for config {key}."
    )
    return final_lines_list, coord_map
