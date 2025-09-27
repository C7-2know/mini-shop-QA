"""
Functional UI tests for MiniShop.
"""

import pytest
from playwright.sync_api import Page, expect

class TestHappyPath:

    @pytest.fixture(scope="function", autouse=True)
    def setup(self, page: Page):
        self.page = page

    @pytest.fixture()
    def login(self, page: Page):
        """Fixture to log in to the application."""
        page.goto("http://localhost:3000")
        page.get_by_role("textbox", name="Username").fill("test")
        page.get_by_role("textbox", name="Password").fill("pass")
        page.get_by_role("button", name="Sign In").click()
        # Ensure login is successful before other tests run
        return page

    def test_login_flow(self, page: Page, login: Page):
        expect(page.get_by_role("button", name="Logout")).to_be_visible()
        

    def test_complete_ecommerce_flow(self, login: Page):
    
        login.get_by_role("button", name="Apply Filters").click()
        # Add more test steps here...

    def test_filter_flow(self, login:Page):        
        # count the number of items with electronics category 
        pre_filter = login.get_by_text('Electronics').count()

        login.get_by_role('textbox', name='Category').fill('Electronics')
    
        # Click the "Apply Filters" button
        login.get_by_role('button', name='Apply Filters').click()
        
        expect(login.get_by_text('Clothing')).not_to_be_visible()
        expect(login.get_by_text('Accessories')).not_to_be_visible()
        expect(login.get_by_text('Electronics')).to_have_count(pre_filter)
    
    def test_add_multiple_items_to_cart(self, login: Page):
        # Add first item to cart
        login.get_by_role("button", name="Add to Cart", exact=True).first.click()

        # Add second item to cart
        login.get_by_role("button", name="Add to Cart", exact=True).nth(1).click()

        # Verify cart count
        expect(login.get_by_role("button", name="Cart (2)")).to_be_visible()
        # Go to cart
        login.get_by_role("button", name="Cart (2)").click()
        # Verify items in cart
        expect(login.get_by_role("heading", name="Shopping Cart")).to_be_visible()
        expect(login.get_by_role("button", name="Remove", exact=True).first).to_be_visible()
        # count remove button
        expect(login.get_by_role("button", name="Remove", exact=True)).to_have_count(2)

    def test_checkout_flow(self, login: Page):
        # Add item to cart
        login.get_by_role("button", name="Add to Cart", exact=True).first.click()

        # Go to cart
        login.get_by_role("button", name="Cart (1)").click()

        # Proceed to checkout
        login.get_by_role("button", name="Proceed to Checkout").click()

        # Fill in checkout details
        # street address, city, zip code, country,  state, Cardholder Name, Card Number, MM/YY, CVV

        login.get_by_role("textbox", name="Street Address").fill("123 Main St")
        login.get_by_role("textbox", name="City").fill("Anytown")
        login.get_by_role("textbox", name="Zip Code").fill("12345")
        login.get_by_role("textbox", name="Country").fill("USA")
        login.get_by_role("textbox", name="State").fill("CA")
        login.get_by_role("textbox", name="Cardholder Name").fill("Test User")
        login.get_by_role("textbox", name="Card Number").fill("4111111111111111")
        login.get_by_role("textbox", name="MM/YY").fill("12/25")
        login.get_by_role("textbox", name="CVV").fill("123")    


        # Submit order
        login.get_by_role("button", name="Complete Order").click()

        # Verify order confirmation

        expect(login.get_by_text("Order Confirmed!")).to_be_visible()
        expect(login.get_by_role("button", name="Continue Shopping")).to_be_visible()
        expect(login.get_by_role("button", name="Logout")).to_be_visible()
  