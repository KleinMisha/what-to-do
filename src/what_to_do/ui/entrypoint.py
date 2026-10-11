"""Main application setup for TUI"""

from what_to_do.db.database import get_engine
from what_to_do.db.schema import Base
from what_to_do.ui.app import WhatToDoApp
from what_to_do.ui.settings import get_tui_settings


def main() -> None:
    """WhatToTUI (what-to-do tui) entrypoint."""
    settings = get_tui_settings()
    Base.metadata.create_all(get_engine(settings.database_url))

    app = WhatToDoApp()
    app.run()


if __name__ == "__main__":
    main()
