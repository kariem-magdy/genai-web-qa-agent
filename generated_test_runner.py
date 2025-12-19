import asyncio
from playwright.async_api import async_playwright

async def test_user_authentication():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com/")

        try:
            # Scenario 1: Verify User Authentication Flow
            print("Testing Scenario 1: Verify User Authentication Flow")
            await page.click("a[href='/login']")
            await page.fill("input[data-qa='signup-name']", "testuser")
            await page.fill("input[data-qa='signup-email']", "testuser123@example.com")
            await page.click("button[data-qa='signup-button']")
            await page.wait_for_url("**/signup**") # Wait for signup page to load

            await page.fill("input[data-qa='login-email']", "testuser123@example.com")
            await page.fill("input[data-qa='login-password']", "password123") # Assuming a default password for signup if not explicitly set. In a real scenario, you'd verify signup password setting.
            await page.click("button[data-qa='login-button']")
            await page.wait_for_selector("a[href='/logout']")
            print("User successfully logged in.")

            await page.click("a[href='/logout']")
            await page.wait_for_url("**/login**") # Wait for login page to load after logout
            print("User successfully logged out.")
            print("Scenario 1 PASSED")

        except Exception as e:
            print(f"Scenario 1 FAILED: {e}")

        finally:
            await browser.close()

async def test_product_browsing_and_cart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com/")

        try:
            # Scenario 2: Verify Product Browsing and Cart Interaction
            print("\nTesting Scenario 2: Verify Product Browsing and Cart Interaction")
            await page.click("a[href='/products']")
            await page.wait_for_url("**/products**")

            # Add a product to the cart (using the first product as an example)
            await page.click(".add-to-cart")
            await page.click(".close-modal") # Close the modal that appears after adding to cart

            # Verify if the cart count is updated (optional, requires more robust selectors for cart count)
            # For simplicity, we'll just navigate to the cart page.
            await page.click("a[href='/view_cart']")
            await page.wait_for_url("**/view_cart**")

            # Assert that a product is present in the cart
            product_in_cart = await page.locator(".cart_description p").count()
            if product_in_cart > 0:
                print("Product successfully added to cart and is visible in the cart.")
                print("Scenario 2 PASSED")
            else:
                print("Product not found in the cart.")
                print("Scenario 2 FAILED")

        except Exception as e:
            print(f"Scenario 2 FAILED: {e}")

        finally:
            await browser.close()

async def test_qa_resources_access():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com/")

        try:
            # Scenario 3: Verify Access to QA Resources
            print("\nTesting Scenario 3: Verify Access to QA Resources")

            # Test Cases link in header
            await page.click("a[href='/test_cases']")
            await page.wait_for_url("**/test_cases**")
            print("Navigated to Test Cases page via header link.")
            await page.go_back() # Go back to home page

            # API Testing link in header
            await page.click("a[href='/api_list']")
            await page.wait_for_url("**/api_list**")
            print("Navigated to API Testing page via header link.")
            await page.go_back() # Go back to home page

            # Test Cases button on slider
            # This button might be within a carousel, so we need to ensure it's visible or wait for it.
            await page.locator(".test_cases_list").click()
            await page.wait_for_url("**/test_cases**")
            print("Navigated to Test Cases page via slider button.")
            await page.go_back() # Go back to home page

            # APIs list for practice button on slider
            await page.locator(".apis_list").click()
            await page.wait_for_url("**/api_list**")
            print("Navigated to API Testing page via slider button.")
            await page.go_back() # Go back to home page

            print("Scenario 3 PASSED")

        except Exception as e:
            print(f"Scenario 3 FAILED: {e}")

        finally:
            await browser.close()

async def main():
    await test_user_authentication()
    await test_product_browsing_and_cart()
    await test_qa_resources_access()

if __name__ == "__main__":
    asyncio.run(main())