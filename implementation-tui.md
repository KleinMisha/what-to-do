# TUI implementation plan

## 1. Setup and boundary conditions

- [x] Install `textual` as a project dependency.
- [ ] Add any required Textual test/development dependencies.
- [x] Register `what-to-tui` as a separate project entry point in `pyproject.toml`.
- [x] Create the `tui/` package and its entry point.
- [x] Create `tui/helpers.py` with `get_tui_client()`.

## 2. Basic main application — `WhatToDoApp`

- [x] Create `tui/app.py`.
- [x] Define `WhatToDoApp(App[None])`.
- [x] Use `get_tui_client()` directly inside panels and resource widgets.
- [x] Open a client context for each operation and close it when finished.
- [x] Let `get_tui_client()` resolve the configured local or remote client.
- [x] Avoid injecting or retaining long-lived clients unless a concrete need arises.
- [x] Add a class variable for keyboard shortcuts; leave it empty initially.
- [x] Set up `compose()` with the two-panel horizontal layout:
  - `ResourceTreePanel` on the left.
  - `ResourceDetailsPanel` on the right.
- [x] Add the basic TUI entry point.
- [x] Add a `__main__` block if appropriate.
- [x] Run the application manually to verify startup and layout.
- [x] Add a minimal application startup test.

## 3. Shared messages — `tui/messages.py`

- [ ] Create `tui/messages.py`.
- [ ] Define `ResourceSelected`, containing:
  - `resource_type: ResourceType`
  - `resource_id: UUID`
- [ ] Define `ResourceCreated`, containing the created resource's type and ID.
- [ ] Define `ResourceDeleted`, containing the deleted resource's type and ID.
- [ ] Add other messages only when a concrete interaction requires them.
- [ ] Keep message classes outside the widget classes so they can be imported without coupling consumers to widget internals.

## 4. Resource tree — `ResourceTreePanel`

### Implementation — `tui/widgets/resource_tree.py`

- [x] Create `tui/widgets/resource_tree.py`.
- [x] Define `ResourceTreePanel`.
- [x] Use Textual's built-in `Tree` directly.
- [ ] Define the node-data type used to identify resources, such as `tuple[ResourceType, UUID]`.
- [x] Load groups through `GroupClient`.
- [x] Load each group's projects through `GroupClient`.
- [ ] Load tasks through `TaskClient` if tasks are included in the tree.
- [x] Build the group/project hierarchy.
- [ ] Place tasks under their appropriate group or project, according to the intended hierarchy.
- [x] Handle an empty tree.
- [x] Handle relevant client/domain errors.
- [x] Add `refresh_tree()` to reload the hierarchy.
- [ ] Handle tree selection events.
- [ ] Emit `ResourceSelected` when the user selects a resource.
- [ ] Ensure expand/collapse operations don't emit unnecessary resource-selection messages.
- [x] Verify keyboard navigation with `↑`/`↓`.
- [x] Run the application manually to verify the populated tree.

### Tests — `tests/tui/test_resource_tree.py`

- [ ] Test that groups are displayed.
- [ ] Test that projects appear under their correct groups.
- [ ] Test that tasks appear in their correct locations, if included.
- [ ] Test that node data contains the correct resource type and ID.
- [ ] Test that selecting a group emits `ResourceSelected` with the correct values.
- [ ] Test that selecting a project emits `ResourceSelected` with the correct values.
- [ ] Test task selection if tasks are included.
- [ ] Test that `refresh_tree()` reflects changes in the underlying data.
- [ ] Test empty-tree behavior.
- [ ] Test relevant loading and client errors.
- [ ] Use Textual's `run_test()` and `Pilot` for interaction tests.

## 5. Resource details panel — `ResourceDetailsPanel`

### Implementation — `tui/widgets/resource_details.py`

- [ ] Create `tui/widgets/resource_details.py`.
- [ ] Define `ResourceDetailsPanel`.
- [ ] Track the currently mounted detail widget using `active_resource`.
- [ ] Implement `set_resource(resource_type, resource_id)`.
- [ ] Dispatch to the appropriate widget:
  - `TaskDetail`
  - `ProjectDetail`
  - `GroupDetail`
- [ ] Remove the previous detail widget when the selection changes.
- [ ] Mount the newly selected widget.
- [ ] Ensure a newly selected resource starts in read mode.
- [ ] Implement `switch_mode("read")` and `switch_mode("edit")`.
- [ ] Delegate mode switching to the active detail widget.
- [ ] Handle the no-selection state.
- [ ] Handle loading and mounting errors without leaving stale details visible.

### Implementation notes

- `ResourceDetailsPanel` owns resource selection and the active widget.
- It should not implement resource-specific fields or form logic.
- Only one resource detail widget should be mounted at a time.
- Use asynchronous mounting/removal where required by Textual.
- Avoid race conditions if the user selects another resource while a previous resource is loading.

### Tests — `tests/tui/test_resource_details.py`

- [ ] Test that selecting a task mounts `TaskDetail`.
- [ ] Test that selecting a project mounts `ProjectDetail`.
- [ ] Test that selecting a group mounts `GroupDetail`.
- [ ] Test that changing selection removes the previous widget.
- [ ] Test that only one detail widget is mounted at a time.
- [ ] Test that the correct resource ID is passed to the widget.
- [ ] Test that a newly selected resource starts in read mode.
- [ ] Test that `switch_mode("edit")` delegates to the active widget.
- [ ] Test that `switch_mode("read")` delegates to the active widget.
- [ ] Test that mode switching without a selected resource is harmless.
- [ ] Test relevant loading errors.

**Acceptance criteria:** The details panel correctly dispatches to resource-specific widgets, replaces the active widget, and delegates mode switching.

## 6. Resource-specific details — `tui/widgets/`

Each resource-specific widget owns its fields, resource loading, and read/edit behavior. Fields are yielded once and become editable or read-only depending on the current mode.

### 6.1 Task details — `tui/widgets/task_detail.py`

- [ ] Create `tui/widgets/task_detail.py`.
- [ ] Define `TaskDetail`.
- [ ] Accept an optional task ID:
  - Existing ID: load an existing task.
  - No ID: prepare to create a task.
- [ ] Load an existing task through `get_tui_client(ResourceType.TASKS)`.
- [ ] Yield task fields once in `compose()`.
- [ ] Populate fields after loading.
- [ ] Start existing tasks in read mode.
- [ ] Start newly created tasks in edit mode.
- [ ] Implement `enter_edit_mode()`.
- [ ] Implement `enter_read_mode()`.
- [ ] Toggle field `read_only` properties rather than recreating the form.
- [ ] Preserve original values when editing so cancellation can restore them.
- [ ] Validate user input.
- [ ] Implement saving through the task client.
- [ ] Emit `ResourceCreated` after successful creation.
- [ ] Emit an update notification after successful modification if other UI components need to react.
- [ ] Implement deletion through the task client.
- [ ] Emit `ResourceDeleted` after successful deletion.
- [ ] Handle validation, loading, saving, and deletion errors.

### 6.2 Project details — `tui/widgets/project_detail.py`

- [ ] Create `tui/widgets/project_detail.py`.
- [ ] Define `ProjectDetail`.
- [ ] Support loading an existing project or creating a new one.
- [ ] Yield project fields once in `compose()`.
- [ ] Populate fields after loading.
- [ ] Implement `enter_edit_mode()` and `enter_read_mode()`.
- [ ] Toggle field `read_only` properties.
- [ ] Preserve original values when editing so cancellation works.
- [ ] Validate and save project changes through the project client.
- [ ] Support group assignment where applicable.
- [ ] Emit `ResourceCreated` after successful creation.
- [ ] Emit an update notification after successful modification if needed.
- [ ] Support deletion and emit `ResourceDeleted` after successful deletion.
- [ ] Handle relevant errors.

### 6.3 Group details — `tui/widgets/group_detail.py`

- [ ] Create `tui/widgets/group_detail.py`.
- [ ] Define `GroupDetail`.
- [ ] Support loading an existing group or creating a new one.
- [ ] Yield group fields once in `compose()`.
- [ ] Populate fields after loading.
- [ ] Implement `enter_edit_mode()` and `enter_read_mode()`.
- [ ] Toggle field `read_only` properties.
- [ ] Preserve original values when editing so cancellation works.
- [ ] Validate and save group changes through the group client.
- [ ] Emit `ResourceCreated` after successful creation.
- [ ] Emit an update notification after successful modification if needed.
- [ ] Support deletion and emit `ResourceDeleted` after successful deletion.
- [ ] Handle relevant errors.

### Tests for resource-specific widgets

- [ ] Test loading and displaying existing resources.
- [ ] Test that existing resources start in read mode.
- [ ] Test that new resources start in edit mode.
- [ ] Test that fields become editable in edit mode.
- [ ] Test that fields become read-only in read mode.
- [ ] Test that cancelling restores original field values.
- [ ] Test saving valid changes.
- [ ] Test that invalid input isn't persisted.
- [ ] Test successful creation and emitted messages.
- [ ] Test successful deletion and emitted messages.
- [ ] Test relevant client/domain errors.

**Acceptance criteria:** Each resource widget can load, display, edit, create, and delete its resource independently of the app's cross-panel coordination.

## 7. Cross-panel coordination — `WhatToDoApp`

### Implementation — `tui/app.py`

- [ ] Handle `ResourceSelected`.
- [ ] Forward the selected resource type and ID to `ResourceDetailsPanel.set_resource()`.
- [ ] Ensure newly selected resources start in read mode.
- [ ] Add an application action for entering edit mode.
- [ ] Bind `E` to the edit action.
- [ ] Add an application action for returning to read mode.
- [ ] Bind `Escape` to cancel editing or return to read mode.
- [ ] Ensure Escape restores original values when cancelling edits.
- [ ] Avoid entering edit mode when no resource is selected.
- [ ] Keep cross-panel coordination in `WhatToDoApp`.
- [ ] Keep resource-specific behavior inside each resource widget.
- [ ] Keep tree-specific behavior inside `ResourceTreePanel`.
- [ ] Keep active-widget and mode management inside `ResourceDetailsPanel`.

### Tests — `tests/tui/test_app.py`

- [ ] Test that selecting a tree node updates the details panel.
- [ ] Test selection of each resource type.
- [ ] Test that `E` enters edit mode.
- [ ] Test that Escape cancels editing.
- [ ] Test that changing resource selection returns to read mode.
- [ ] Test that mode switching without a selection is harmless.

**Acceptance criteria:** Selecting resources and switching modes works through the application without panels directly manipulating each other's internals.

## 8. Resource creation and updates

### Creation flow

- [ ] Add application actions for creating tasks, projects, and groups.
- [ ] Define a clear way to initiate resource creation, such as a command or keybinding.
- [ ] Have `WhatToDoApp` coordinate the creation action.
- [ ] Tell `ResourceDetailsPanel` to mount the appropriate resource widget without an existing ID.
- [ ] Start the new resource widget in edit mode.
- [ ] Keep the tree unchanged while the resource is unsaved initially.
- [ ] Validate required fields before saving.
- [ ] Persist the new resource only after the user saves.
- [ ] Emit `ResourceCreated` after successful persistence.
- [ ] Handle `ResourceCreated` in `WhatToDoApp`.
- [ ] Refresh the tree after creation.
- [ ] Select the newly created resource in the tree.
- [ ] Load the saved resource into the details panel in read mode.
- [ ] Handle cancellation without creating a database record.
- [ ] Handle failed creation without losing the user's entered values.

### Updates

- [ ] Save changes through the relevant resource client.
- [ ] Return the widget to read mode after a successful save.
- [ ] Ensure the displayed values reflect the saved resource.
- [ ] Refresh the tree if the updated fields affect its labels or hierarchy.
- [ ] Avoid unnecessary detail reloads when the active widget already holds the updated resource.

### Tests

- [ ] Test that creating a resource opens the correct form in edit mode.
- [ ] Test that cancelling creation does not persist a resource.
- [ ] Test successful creation and tree refresh.
- [ ] Test that the newly created resource becomes selected.
- [ ] Test that the details panel displays the saved resource in read mode.
- [ ] Test failed creation and preservation of entered values.
- [ ] Test updates and any required tree refreshes.

**Acceptance criteria:** Creation and updates keep the tree and details panel synchronized.

## 9. Resource deletion and fallback selection

### Implementation

- [ ] Add a delete action to resource detail widgets.
- [ ] Ask for confirmation before deletion.
- [ ] Delete through the relevant resource client.
- [ ] Emit `ResourceDeleted` only after successful deletion.
- [ ] Handle `ResourceDeleted` in `WhatToDoApp`.
- [ ] Refresh the resource tree.
- [ ] Determine which resource should be selected next.
- [ ] Select the fallback node in the refreshed tree.
- [ ] Load the fallback resource in the details panel in read mode.
- [ ] Show the details panel's empty state if no resources remain.
- [ ] Handle deletion errors without discarding the current selection.

### Fallback-selection behavior

- [ ] Prefer the previous selectable sibling, if available.
- [ ] Otherwise select the parent group if it still exists.
- [ ] Otherwise select the next available resource.
- [ ] If no selectable resources remain, clear the selection and show an empty state.

Capture enough information before deletion to determine the fallback after the tree is rebuilt.

### Tests

- [ ] Test that deletion removes the resource from the tree.
- [ ] Test fallback selection after deletion.
- [ ] Test that the details panel displays the fallback resource.
- [ ] Test deletion when no fallback exists.
- [ ] Test that failed deletion leaves the current selection intact.

**Acceptance criteria:** Deleting a resource leaves the UI in a consistent state.

## 10. Command palette and keyboard shortcuts

- [ ] Integrate Textual's command palette.
- [ ] Add the initial command palette structure.
- [ ] Add keyboard shortcut configuration.
- [ ] Add navigation actions.
- [ ] Add resource creation actions.
- [ ] Add resource editing and saving actions.
- [ ] Add resource deletion actions.
- [ ] Make command-palette actions and keyboard shortcuts invoke the same application actions.
- [ ] Avoid duplicating business logic between commands and keybindings.

## 11. Integration tests

- [ ] Test that the application starts successfully.
- [ ] Test that groups and projects appear in the resource tree.
- [ ] Test tree keyboard navigation using Textual's `Pilot`.
- [ ] Test that selecting each resource type updates the details panel.
- [ ] Test that only one detail widget is mounted at a time.
- [ ] Test switching between read and edit modes.
- [ ] Test creation and cancellation.
- [ ] Test that successful creation refreshes and selects the new resource.
- [ ] Test updates and any required tree refresh.
- [ ] Test deletion and fallback selection.
- [ ] Test important empty and error states.
- [ ] Test keyboard shortcuts and command-palette actions.
- [ ] Focus tests on observable behavior rather than Textual internals.

## 12. CSS and responsive layout

- [ ] Create `tui/styles/app.tcss`.
- [x] Use a two-panel horizontal layout.
- [ ] Set appropriate widths for the tree and details panels.
- [ ] Add focus styling.
- [ ] Add selection styling.
- [ ] Style the status bar if one is added.
- [ ] Improve empty/loading/error states.
- [ ] Implement the narrow-terminal layout.
- [ ] Hide or collapse `ResourceTreePanel` at narrow widths if necessary.
- [ ] Add a mechanism for showing/hiding the resource tree on narrow terminals.
- [ ] Refine colors, spacing, borders, and typography.
- [ ] Run manual checks at wide and narrow terminal sizes.

## 13. Makefile and installation

- [ ] Add `install-tui-local`.
- [ ] Install/update the application through the existing installation mechanism.
- [ ] Configure the local client if necessary.
- [ ] Ensure the database/data directory is created on first actual use.
- [ ] Launch the TUI through `what-to-tui`.
- [ ] Add installation status messages consistent with the CLI.
- [ ] Decide whether a separate TUI uninstall target is necessary.
- [ ] If needed, remove TUI configuration while preserving the user's database.

## 14. Final verification

- [ ] Run the complete test suite.
- [ ] Run the application through `what-to-tui`.
- [ ] Verify tree navigation and resource selection.
- [ ] Verify read/edit/cancel/save behavior for each resource type.
- [ ] Verify resource creation and deletion.
- [ ] Verify fallback selection after deletion.
- [ ] Verify empty states and error handling.
- [ ] Verify behavior at wide and narrow terminal sizes.
- [ ] Check for regressions in the existing CLI and API.