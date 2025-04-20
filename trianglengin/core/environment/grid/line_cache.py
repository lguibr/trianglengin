# File: trianglengin/core/environment/grid/line_cache.py
import logging
from typing import Final

from trianglengin.config.env_config import EnvConfig

log = logging.getLogger(__name__)

# Type alias for coordinate tuple
Coord = tuple[int, int]
# Type alias for a line (tuple of coordinates)
Line = tuple[Coord, ...]
# Type alias for the coordinate-to-lines map value
LineSet = set[frozenset[Coord]]
# Type alias for the coordinate-to-lines map
CoordMap = dict[Coord, LineSet]
# Type alias for the cache key
ConfigKey = tuple[
    int, int, tuple[tuple[int, int], ...], int
]  # Key now includes tuple of tuples
# Type alias for the cached value (lines list and coord map)
CachedData = tuple[list[Line], CoordMap]
# Cache: Maps config key to cached data
_LINE_CACHE: dict[ConfigKey, CachedData] = {}

# --- Constants for Directions ---
HORIZONTAL: Final = "h"
DIAGONAL_TL_BR: Final = "d1"
DIAGONAL_BL_TR: Final = "d2"


def _create_cache_key(config: EnvConfig) -> ConfigKey:
    """Creates an immutable cache key from relevant EnvConfig fields."""
    return (
        config.ROWS,
        config.COLS,
        tuple(tuple(item) for item in config.PLAYABLE_RANGE_PER_ROW),
        config.MIN_LINE_LENGTH,
    )


def get_precomputed_lines_and_map(config: EnvConfig) -> CachedData:
    """
    Retrieves the precomputed lines and the coordinate-to-lines map
    for a given configuration, using a cache.

    Args:
        config: The environment configuration.

    Returns:
        A tuple containing:
            - List[Line]: A list of lines (tuples of coordinates).
            - CoordMap: A dictionary mapping coordinates to sets of lines (frozensets)
                        they belong to.
    """
    key = _create_cache_key(config)
    if key not in _LINE_CACHE:
        log.info(f"Cache miss for grid config: {key}. Computing lines and map.")
        _LINE_CACHE[key] = _compute_lines_and_map_for_config(config)

    lines, coord_map = _LINE_CACHE[key]
    return list(lines), {coord: set(lineset) for coord, lineset in coord_map.items()}


def _compute_lines_and_map_for_config(config: EnvConfig) -> CachedData:
    """
    Computes all lines (including sub-lines >= min_len) and the coordinate-to-lines map.
    Uses PLAYABLE_RANGE_PER_ROW for validity checks.
    """
    rows, cols = config.ROWS, config.COLS
    min_len = config.MIN_LINE_LENGTH
    final_lines_set: set[Line] = set()

    def is_live(r: int, c: int) -> bool:
        """Checks if a cell is within bounds and the playable range for its row."""
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        start_col, end_col = config.PLAYABLE_RANGE_PER_ROW[r]
        return start_col <= c < end_col

    # Iterate through each cell as a potential start of a line segment
    for r_start in range(rows):
        for c_start in range(cols):
            if not is_live(r_start, c_start):
                continue

            # --- Horizontal ---
            line_h: list[Coord] = []
            for c_curr in range(c_start, cols):
                if is_live(r_start, c_curr):
                    line_h.append((r_start, c_curr))
                    if len(line_h) >= min_len:
                        final_lines_set.add(tuple(line_h))
                else:
                    break

            # --- Diagonal TL-BR ---
            line_d1: list[Coord] = []
            cr, cc = r_start, c_start
            while is_live(cr, cc):
                line_d1.append((cr, cc))
                if len(line_d1) >= min_len:
                    final_lines_set.add(tuple(line_d1))
                is_up = (cr + cc) % 2 != 0
                next_r, next_c = (cr + 1, cc) if is_up else (cr, cc + 1)
                cr, cc = next_r, next_c

            # --- Diagonal BL-TR ---
            line_d2: list[Coord] = []
            cr, cc = r_start, c_start
            while is_live(cr, cc):
                line_d2.append((cr, cc))
                if len(line_d2) >= min_len:
                    final_lines_set.add(tuple(line_d2))
                is_up = (cr + cc) % 2 != 0
                next_r, next_c = (cr - 1, cc) if not is_up else (cr, cc + 1)
                cr, cc = next_r, next_c

    final_lines_list = sorted(
        final_lines_set,
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
        f"Computed {len(final_lines_list)} unique lines (min_len={min_len}) and map for {len(coord_map)} coords for config {key}."
    )
    return final_lines_list, coord_map
