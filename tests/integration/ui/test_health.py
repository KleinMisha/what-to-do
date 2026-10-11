import pytest

from what_to_do.ui.app import WhatToDoApp


@pytest.mark.asyncio
async def test_app_starts() -> None:
    app = WhatToDoApp()

    async with app.run_test():
        assert app.query_one("#left-panel")
        assert app.query_one("#middle-panel")
        assert app.query_one("#right-panel")
        assert app.is_running
