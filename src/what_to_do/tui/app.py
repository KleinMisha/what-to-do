"""Main TUI application widget: does orchestration between panels"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Label, Static

from what_to_do.tui.widgets.resource_tree import ResourceTreePanel


class DummyPanel(Static):
    def __init__(self, id: str, text: str) -> None:
        super().__init__(id=id)
        self.text = text

    def compose(self) -> ComposeResult:
        yield Label(self.text)


class WhatToDoApp(App[None]):
    """Main application"""

    # Define your shortcuts: (key, action, description)
    BINDINGS = [  # noqa: RUF012
        ("ctrl+b", "toggle_tree", "Toggle resource tree"),
        ("q", "quit", "Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="resource-tree-panel"):
                yield ResourceTreePanel()

            with Vertical(id="task-details"):
                yield DummyPanel(id="right-panel", text="right-panel")

        yield Footer(id="keybindings")

    def action_toggle_tree(self) -> None:
        tree_panel = self.query_one(
            "#resource-tree-panel",
            Vertical,
        )
        tree_panel.display = not tree_panel.display
