import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        url = "https://practicetestautomation.com/practice-test-login/"

        # Test Scenario 1: Verify Successful Login
        print("--- Running Test Scenario 1: Verify Successful Login ---")
        try:
            await page.goto(url)
            await page.locator("#username").fill("student")
            await page.locator("#password").fill("Password123")
            await page.locator("#submit").click()
            await page.wait_for_url("**/logged-in-successfully/")
            assert "Congratulations" in await page.inner_text("h1")
            assert await page.locator("text=Log out").is_visible()
            print("Test Scenario 1 PASSED")
        except Exception as e:
            print(f"Test Scenario 1 FAILED: {e}")

        # Test Scenario 2: Verify Error Message for Invalid Login (Incorrect Username)
        print("\n--- Running Test Scenario 2: Verify Error Message for Invalid Login (Incorrect Username) ---")
        try:
            await page.goto(url)
            await page.locator("#username").fill("incorrectUser")
            await page.locator("#password").fill("Password123")
            await page.locator("#submit").click()
            error_message = await page.locator("#error").inner_text()
            assert error_message == "Your username is invalid!"
            print("Test Scenario 2 PASSED")
        except Exception as e:
            print(f"Test Scenario 2 FAILED: {e}")

        # Test Scenario 3: Verify Error Message for Invalid Login (Incorrect Password)
        print("\n--- Running Test Scenario 3: Verify Error Message for Invalid Login (Incorrect Password) ---")
        try:
            await page.goto(url)
            await page.locator("#username").fill("student")
            await page.locator("#password").fill("incorrectPassword")
            await page.locator("#submit").click()
            error_message = await page.locator("#error").inner_text()
            assert error_message == "Your password is invalid!"
            print("Test Scenario 3 PASSED")
        except Exception as e:
            print(f"Test Scenario 3 FAILED: {e}")

        # Test Scenario 4: Verify Navigation to Home Page
        print("\n--- Running Test Scenario 4: Verify Navigation to Home Page ---")
        try:
            await page.goto(url)
            await page.locator("a[href='https://practicetestautomation.com/']").click()
            await page.wait_for_url("https://practicetestautomation.com/")
            assert "Practice Test Automation" in await page.title()
            print("Test Scenario 4 PASSED")
        except Exception as e:
            print(f"Test Scenario 4 FAILED: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())