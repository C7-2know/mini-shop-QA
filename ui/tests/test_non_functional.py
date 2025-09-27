"""
Non-functional UI tests for MiniShop.
"""

import pytest
from playwright.sync_api import Page, expect

class TestNonFunctional:
    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        self.page = page
        self.url = "http://localhost:3000"

    @pytest.fixture()
    def login(self, page: Page):
        """Fixture to log in to the application."""
        page.goto(self.url)
        page.get_by_role("textbox", name="Username").fill("test")
        page.get_by_role("textbox", name="Password").fill("pass")
        page.get_by_role("button", name="Sign In").click()
        return page
    
    def test_performance_of_homepage_load(self, page: Page):
        page.goto(self.url)
        performance_timing = page.evaluate("JSON.stringify(window.performance.timing)")
        timing = eval(performance_timing)
        load_time = timing['loadEventEnd'] - timing['navigationStart']
        print(f"Homepage load time: {load_time} ms")
        assert load_time < 3000  # Assert that load time is under 3 seconds

    def test_page_load_without__console_error(self, login: Page):
        console_messages = []

        def handle_console(msg):
            if msg.type == "error":
                console_messages.append(msg.text)

        login.on("console", handle_console)
        login.goto(self.url)
        assert len(console_messages) == 0, f"Console errors found: {console_messages}"