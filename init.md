Okay, let's create a detailed plan for refactoring the common components into a single library, `trianglengin`, focusing on the backend logic and deferring visualization changes.

**Project Goal:** Create a reusable Python library named `trianglengin` containing the core game logic, utilities, feature extraction, and data management framework currently duplicated or similar in `AlphaTriangle` and `MuzeroTriangle`. This library will be installable via pip and used as a dependency by both main projects.

**Target Library:** `trianglengin`

**Components to Decouple into `trianglengin`:**

1.  **Core Game Logic:** Environment rules, state representation, actions.
2.  **Utilities:** General helpers, SumTree, geometry functions, shared types.
3.  **Statistics Collection:** The `StatsCollectorActor`.
4.  **Feature Extraction:** Logic to convert game state to NN input format.
5.  **Data Management Framework:** Structure for saving/loading checkpoints and buffers.

**Components Remaining in Main Projects (`AlphaTriangle`, `MuzeroTriangle`):**

1.  **NN Architecture:** `nn` module (specific models like `AlphaTriangleNet`, `MuZeroNet`).
2.  **MCTS Implementation:** `mcts` module (specific search strategies).
3.  **RL Algorithm:** `rl` module (Trainer, Buffer implementation, Worker implementation, algorithm-specific types like `Experience` or `TrajectoryStep`).
4.  **Training Orchestration:** `training` module (Loop, specific setup, runners).
5.  **Configuration:** Algorithm-specific configs (`ModelConfig`, `TrainConfig`, `MCTSConfig`). `EnvConfig` and `PersistenceConfig` will likely move to `trianglengin`.
6.  **Visualization & Interaction:** `visualization`, `interaction`, `app` (Deferred for later refactoring/replacement).
7.  **CLI:** `cli` module (project-specific commands).

---

## `trianglengin` Library Structure Plan

```
trianglengin/
├── trianglengin/
│   ├── __init__.py           # Exposes public API
│   ├── core/                 # Core game logic
│   │   ├── __init__.py
│   │   ├── structs/          # Triangle, Shape, constants
│   │   │   ├── __init__.py
│   │   │   ├── constants.py
│   │   │   ├── shape.py
│   │   │   └── triangle.py
│   │   └── environment/      # GameState, GridData, GridLogic, ShapeLogic, ActionCodec
│   │       ├── __init__.py
│   │       ├── action_codec.py
│   │       ├── game_state.py
│   │       ├── grid_data.py
│   │       └── logic.py      # Renamed from grid/logic.py & shapes/logic.py? Needs review. Maybe keep grid/shapes subdirs? -> Keep grid/shapes subdirs for clarity.
│   │       ├── grid/
│   │       │   ├── __init__.py
│   │       │   ├── grid_data.py # Moved here
│   │       │   └── logic.py
│   │       └── shapes/
│   │           ├── __init__.py
│   │           ├── logic.py
│   │           └── templates.py
│   │       └── logic/            # Higher-level game logic (valid actions, step execution)
│   │           ├── __init__.py
│   │           ├── actions.py
│   │           └── step.py
│   ├── features/             # Feature extraction logic
│   │   ├── __init__.py
│   │   ├── extractor.py
│   │   └── grid_features.py
│   ├── data/                 # Data management framework
│   │   ├── __init__.py
│   │   ├── data_manager.py
│   │   ├── path_manager.py
│   │   ├── serializer.py
│   │   └── schemas.py        # Base schemas (BaseCheckpointData, BaseBufferData)
│   ├── stats/                # Statistics collection actor
│   │   ├── __init__.py
│   │   └── collector.py      # StatsCollectorActor
│   ├── utils/                # General utilities
│   │   ├── __init__.py
│   │   ├── geometry.py
│   │   ├── helpers.py
│   │   ├── sumtree.py
│   │   └── types.py          # Shared, generic types (ActionType, StepInfo, etc.)
│   └── config/               # Shared configuration models
│       ├── __init__.py
│       ├── env_config.py
│       └── persistence_config.py
├── tests/                    # Unit tests for trianglengin components
│   ├── __init__.py
│   ├── conftest.py           # Shared test fixtures for trianglengin
│   ├── core/
│   │   ├── __init__.py
│   │   ├── structs/
│   │   └── environment/
│   ├── features/
│   ├── data/
│   ├── stats/
│   └── utils/
├── pyproject.toml            # Build config, dependencies (pydantic, numpy, ray, etc.)
├── README.md
├── LICENSE
└── MANIFEST.in
```

---

## Detailed Refactoring Plan

**Phase 0: Project Setup (`trianglengin`)**

1.  **Create Directory Structure:** Set up the `trianglengin` project folder and internal structure as outlined above.
2.  **Initialize `pyproject.toml`:** Define build system, project metadata (name, version, author), dependencies (`pydantic`, `numpy`, `ray`, `cloudpickle`, `numba`, `mlflow`, `typing_extensions`). Ensure Python version constraint (`>=3.10`).
3.  **Add `LICENSE`, `README.md`, `MANIFEST.in`.**
4.  **Setup Testing:** Configure `pytest` in `pyproject.toml`. Create `tests/conftest.py` for shared fixtures within the library. Set up Ruff and MyPy configurations.

**Phase 1: Core Game Logic (`trianglengin.core`)**

1.  **Move `structs`:** Copy the entire `structs` directory (constants, shape, triangle) from one of the projects into `trianglengin/core/structs/`.
2.  **Move `environment`:** Copy the relevant parts of the `environment` module:
    *   `environment/core/action_codec.py` -> `trianglengin/core/environment/action_codec.py`
    *   `environment/core/game_state.py` -> `trianglengin/core/environment/game_state.py`
    *   `environment/grid/grid_data.py` -> `trianglengin/core/environment/grid/grid_data.py`
    *   `environment/grid/logic.py` -> `trianglengin/core/environment/grid/logic.py`
    *   `environment/shapes/logic.py` -> `trianglengin/core/environment/shapes/logic.py`
    *   `environment/shapes/templates.py` -> `trianglengin/core/environment/shapes/templates.py`
    *   `environment/logic/actions.py` -> `trianglengin/core/environment/logic/actions.py`
    *   `environment/logic/step.py` -> `trianglengin/core/environment/logic/step.py`
3.  **Move `EnvConfig`:** Move `config/env_config.py` to `trianglengin/config/env_config.py`.
4.  **Update Imports within `trianglengin`:** Adjust all relative imports within the moved files to reflect the new structure (e.g., `from ...structs import Shape`, `from ...config import EnvConfig`).
5.  **Expose Public API:** Update `trianglengin/core/__init__.py`, `trianglengin/core/structs/__init__.py`, `trianglengin/core/environment/__init__.py`, etc., to export the necessary classes and functions (`GameState`, `GridData`, `Shape`, `Triangle`, `EnvConfig`, `encode_action`, `decode_action`, etc.).
6.  **Add Unit Tests:** Create tests in `tests/core/` for `GameState`, `GridLogic`, `ShapeLogic`, `ActionCodec`, ensuring game rules, state transitions, and action encoding work correctly. Use the `EnvConfig` from `trianglengin.config`.
7.  **Refactor Main Projects (Alpha/Muzero):**
    *   Add `trianglengin` as a dependency (initially using an editable install: `pip install -e ../trianglengin`).
    *   Remove the duplicated `structs` and `environment` directories.
    *   Update all imports to use `trianglengin.core.structs` and `trianglengin.core.environment`.
    *   Update imports for `EnvConfig` to use `trianglengin.config`.
    *   Run existing environment tests in the main projects to ensure they still pass using the library code. Adapt tests if necessary due to import changes.

**Phase 2: Utilities & Stats Collector (`trianglengin.utils`, `trianglengin.stats`)**

1.  **Move Utilities:**
    *   `utils/helpers.py` -> `trianglengin/utils/helpers.py`
    *   `utils/geometry.py` -> `trianglengin/utils/geometry.py`
    *   `utils/sumtree.py` -> `trianglengin/utils/sumtree.py`
2.  **Move Shared Types:** Identify types used by multiple decoupled components (e.g., `ActionType`, `StepInfo`, `StatsCollectorData`) and move their definitions to `trianglengin/utils/types.py`. Algorithm-specific types (`Experience`, `TrajectoryStep`, `StateType`, `PERBatchSample`) remain in the main projects for now.
3.  **Move Stats Collector:** Move `stats/collector.py` (`StatsCollectorActor`) to `trianglengin/stats/collector.py`.
    *   *Interface Consideration:* `StatsCollectorActor.update_worker_game_state` currently takes a `GameState`. This creates a dependency on `trianglengin.core`. This is acceptable for now, as visualization is deferred. If visualization is refactored later to not need the full `GameState`, this dependency could potentially be removed.
4.  **Update Imports within `trianglengin`:** Adjust imports in `StatsCollectorActor` and other moved files.
5.  **Expose Public API:** Update `trianglengin/utils/__init__.py` and `trianglengin/stats/__init__.py`.
6.  **Add Unit Tests:** Create tests in `tests/utils/` for helpers and `SumTree`. Create tests in `tests/stats/` for `StatsCollectorActor` (requires `ray` for testing).
7.  **Refactor Main Projects:**
    *   Remove duplicated `utils` files and `stats/collector.py`.
    *   Update imports to use `trianglengin.utils` and `trianglengin.stats`.
    *   Ensure main project tests related to these utilities and the stats actor still pass.

**Phase 3: Feature Extraction (`trianglengin.features`)**

1.  **Move `features`:** Copy `features/extractor.py` and `features/grid_features.py` to `trianglengin/features/`.
2.  **Interface Definition:**
    *   The main function `extract_state_features` needs `GameState` (from `trianglengin.core`) and `ModelConfig`.
    *   `ModelConfig` is algorithm-specific and remains in the main projects.
    *   **Solution:** `extract_state_features` will accept the `ModelConfig` object (or a relevant subset/protocol if defined later) as an argument. The *caller* (in the main project, likely the `SelfPlayWorker` or `NeuralNetwork` wrapper) is responsible for passing the correct configuration.
    *   The return type `StateType` is also specific to the NN input format. For now, `extract_state_features` will return `dict[str, np.ndarray]`, and the main projects will cast/validate this against their specific `StateType` definition.
3.  **Update Imports within `trianglengin`:** Adjust imports in `extractor.py` and `grid_features.py` to use `trianglengin.core.structs`, etc.
4.  **Expose Public API:** Update `trianglengin/features/__init__.py`.
5.  **Add Unit Tests:** Create tests in `tests/features/` for `extract_state_features` and `grid_features`. These tests will need to create mock `GameState` objects (using `trianglengin.core`) and mock `ModelConfig` objects (or dicts) providing the necessary fields (`GRID_INPUT_CHANNELS`, `OTHER_NN_INPUT_FEATURES_DIM`).
6.  **Refactor Main Projects:**
    *   Remove the `features` directory.
    *   Update imports to use `trianglengin.features`.
    *   Ensure calls to `extract_state_features` pass the project's specific `ModelConfig`.
    *   Verify that the returned dictionary structure matches the project's `StateType` definition.
    *   Run existing tests that rely on feature extraction.

**Phase 4: Data Management Framework (`trianglengin.data`)**

1.  **Move Framework Components:**
    *   `data/path_manager.py` -> `trianglengin/data/path_manager.py`
    *   `data/serializer.py` -> `trianglengin/data/serializer.py`
    *   `data/data_manager.py` -> `trianglengin/data/data_manager.py`
2.  **Move `PersistenceConfig`:** Move `config/persistence_config.py` to `trianglengin/config/persistence_config.py`.
3.  **Define Base Schemas:** In `trianglengin/data/schemas.py`, define base Pydantic models:
    *   `BaseCheckpointData`: Includes common fields like `run_name`, `global_step`, `episodes_played`, `total_simulations_run`, `model_config_dict`, `env_config_dict`, `stats_collector_state`. It will *not* include `model_state_dict` or `optimizer_state_dict` directly, as their structure might vary slightly, or they can be handled as `dict[str, Any]`.
    *   `BaseBufferData`: Could be as simple as `buffer_content: Any` or `buffer_list: list[Any]`. This allows flexibility for storing different buffer types (deque, list of experiences, list of trajectories).
    *   `LoadedTrainingState`: Uses `BaseCheckpointData | None` and `BaseBufferData | None`.
4.  **Adapt `DataManager`:**
    *   Modify `save_training_state` to accept the *concrete* data objects (NN state dict, optimizer state dict, buffer object, stats state dict) as arguments. It will construct a `BaseCheckpointData` (or a subclass provided by the main project) and a `BaseBufferData` (or subclass).
    *   It will use `Serializer` to save these Pydantic models. `Serializer.prepare_buffer_data` might need to become more generic or be handled differently (e.g., `DataManager` calls `serializer.save_object(buffer_obj, path)` directly for the buffer). Let's stick to saving a `BaseBufferData` model created by `DataManager` calling a helper (maybe still in `Serializer`?) `prepare_base_buffer_data(buffer_obj) -> BaseBufferData`.
    *   Modify `load_initial_state` to load using `Serializer` and return `LoadedTrainingState` containing the base schemas. The main project is responsible for interpreting the `buffer_content` or `buffer_list` from `BaseBufferData`.
5.  **Adapt `Serializer`:**
    *   Ensure `load/save_checkpoint` and `load/save_buffer` work with the base Pydantic schemas.
    *   Implement `prepare_base_buffer_data(buffer_obj: Any) -> BaseBufferData`: This needs to extract the core data (e.g., convert deque to list) into the `BaseBufferData` structure.
    *   `prepare_optimizer_state` remains the same.
6.  **Update Imports within `trianglengin`:** Adjust imports.
7.  **Expose Public API:** Update `trianglengin/data/__init__.py` and `trianglengin/config/__init__.py`.
8.  **Add Unit Tests:** Create tests in `tests/data/` for `PathManager`, `Serializer`, and `DataManager`. Mock the components (`nn`, `optimizer`, `buffer`, `stats_actor`) passed to `DataManager`. Test saving and loading with the base schemas.
9.  **Refactor Main Projects:**
    *   Remove the `data` directory and `PersistenceConfig`.
    *   Update imports to use `trianglengin.data` and `trianglengin.config`.
    *   Adapt the training setup (`training/setup.py` or runners) to instantiate and use `trianglengin.data.DataManager`.
    *   Modify the loading logic (`_load_and_apply_initial_state`) to handle the `LoadedTrainingState` with base schemas. Specifically, reconstruct the project's `ExperienceBuffer` from the `buffer_list` in `BaseBufferData`.
    *   Modify the saving logic in `TrainingLoop` or runners to call `data_manager.save_training_state` with the correct arguments.
    *   Define concrete `CheckpointData` and `BufferData` schemas *within the main projects* if needed (e.g., inheriting from the base schemas or just for internal use before passing data to `DataManager`).
    *   Run existing tests related to saving/loading.

**Phase 5: Packaging and Final Integration**

1.  **Build `trianglengin`:** Use `python -m build` to create wheel and sdist packages.
2.  **Publish (Optional):** Publish to PyPI or a private registry.
3.  **Install in Main Projects:** Replace editable installs with proper installation (`pip install trianglengin` or from the registry/local wheel).
4.  **Final Cleanup:** Remove any remaining duplicated code or unused imports from `AlphaTriangle` and `MuzeroTriangle`.
5.  **Comprehensive Testing:** Run the *full* test suites for `AlphaTriangle` and `MuzeroTriangle` to ensure everything integrates correctly. Run short training sessions for both projects to verify functionality.

**Phase 6: Documentation**

1.  **`trianglengin` README:** Write a comprehensive README explaining the library's purpose, structure, API, and how to use it. Include installation instructions.
2.  **Submodule READMEs:** Update/create READMEs for each submodule within `trianglengin` detailing its specific purpose and API.
3.  **Main Project READMEs:** Update the READMEs of `AlphaTriangle` and `MuzeroTriangle` to reflect the use of `trianglengin` as a dependency and remove descriptions of the moved components.

---

**Testing Strategy:**

*   **`trianglengin`:** Focus on unit tests for each component (game logic, utils, features, data framework) in isolation. Use mocking where necessary (e.g., mocking `ray` for `StatsCollectorActor` tests if run outside Ray).
*   **`AlphaTriangle`/`MuzeroTriangle`:** Focus on integration tests. Ensure that the main projects can correctly use the `trianglengin` library components. Existing tests should be adapted to use the library's interfaces. End-to-end tests (short training runs) are crucial.

**Potential Challenges & Considerations:**

*   **Type Hinting:** Maintaining consistent and accurate type hints across library boundaries, especially for complex objects like `StateType` or buffer contents. Using protocols or generic base classes might be needed eventually but adds complexity.
*   **Configuration Passing:** Deciding the best way to pass necessary configuration (`ModelConfig`) to decoupled modules like `features`. Passing the whole object is simplest but creates a tighter coupling. Passing only required fields is cleaner but requires more interface management.
*   **Serialization Compatibility:** Ensuring `cloudpickle` can handle all necessary objects, especially when saving/loading state involving the library components from the main projects.
*   **Dependency Management:** Keeping dependencies aligned between `trianglengin` and the main projects.
*   **Performance:** Ensure decoupling doesn't introduce significant performance overhead, especially in critical paths like feature extraction.

This detailed plan provides a phased approach to creating the `trianglengin` library, focusing on clear interfaces and testability while deferring the visualization overhaul.