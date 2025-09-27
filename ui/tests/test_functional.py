"""
Functional UI tests for MiniShop.
"""

import pytest
from playwright.sync_api import Page, expect

class TestFunctional:
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

    
    def test_complete_ecommerce_flow(self, login: Page):
        login.get_by_role("button", name="Apply Filters").click()
        # Add more test steps here...

    def test_filter_by_catagory(self, login:Page):        
        # count the number of items with electronics category 
        pre_filter = login.get_by_text('Electronics').count()
        login.get_by_role('textbox', name='Category').fill('Electronics')

        # Click the "Apply Filters" button
        login.get_by_role('button', name='Apply Filters').click()

        expect(login.get_by_text('Clothing')).not_to_be_visible()
        expect(login.get_by_text('Accessories')).not_to_be_visible()
        expect(login.get_by_text('Electronics')).to_have_count(pre_filter)
    
    def test_by_price_range(self, login:Page):
        #  get first item's price
        price = login.get_by_text('$').first.inner_text()
        price_value = float(price.replace('$', ''))

        min_price = price_value + 10

        login.get_by_placeholder('Min Price').fill(str(min_price))
        login.get_by_placeholder('Max Price').fill('150')


        # Click the "Apply Filters" button
        login.get_by_role('button', name='Apply Filters').click()

        expect(login.get_by_text(f'${min_price}')).not_to_be_visible()
        expect(login.get_by_text('$49.99')).not_to_be_visible()
        expect(login.get_by_text('$199.99')).not_to_be_visible()