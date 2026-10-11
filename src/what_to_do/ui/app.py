"""Main TUI application widget: does orchestration between panels"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Label, Static


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
        ("q", "quit", "Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="resource-tree"):
                yield DummyPanel(id="left-panel", text="left-panel")

            with Vertical(id="task-list"):
                yield DummyPanel(id="middle-panel", text="middle-panel")

            with Vertical(id="task-details"):
                yield DummyPanel(id="right-panel", text="right-panel")

        yield Footer(id="keybindings")
