import pytest
from playwright.sync_api import Page, expect

class TestNegativeCases:

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
    
    def test_invalid_login(self, page: Page):
        page.goto(self.url)
        page.get_by_role("textbox", name="Username").fill("invalid_user")
        page.get_by_role("textbox", name="Password").fill("wrong_pass")
        page.get_by_role("button", name="Sign In").click()
        expect(page.get_by_text("Invalid username or password")).to_be_visible()
    
    def test_address_required_for_checkout(self, login: Page):
        login.get_by_role("button", name="Add to Cart", exact=True).first.click()
        login.get_by_role("button", name="Cart (1)").click()
        login.get_by_role("button", name="Proceed to Checkout").click()

        # Attempt to proceed without filling address
        login.get_by_role("textbox", name="Street Address").fill("123 Main St")
        login.get_by_role("textbox", name="City").fill("Anytown")
        login.get_by_role("textbox", name="Country").fill("USA")
        login.get_by_role("textbox", name="State").fill("CA")
        login.get_by_role("textbox", name="Cardholder Name").fill("Test User")
        login.get_by_role("textbox", name="Card Number").fill("4111111111111111")
        login.get_by_role("textbox", name="MM/YY").fill("12/25")
        login.get_by_role("textbox", name="CVV").fill("123")    


        login.get_by_role("button", name="Complete Order").click()

        expect(login.get_by_text("Zip code is required")).to_be_visible()
    
    