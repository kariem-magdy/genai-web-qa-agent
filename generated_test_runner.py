import asyncio
from playwright.async_api import async_playwright, expect

URL = "https://practicetestautomation.com/practice-test-login/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # --- Scenario 1: Verify Positive Login with Valid Credentials ---
        print("Running Scenario 1: Verify Positive Login with Valid Credentials...")
        try:
            await page.goto(URL)
            await page.fill('#username', 'student')
            await page.fill('#password', 'Password123')
            await page.click('#submit')

            # Expect redirection to the success page URL
            await expect(page).to_have_url("https://practicetestautomation.com/logged-in-successfully/")
            # Expect success message on the new page. The test plan suggests 'Congratulations' or 'successfully logged in'.
            # Assuming 'Congratulations' is present in an H1 tag based on typical success page structures.
            await expect(page.locator('h1')).to_have_text('Congratulations')
            print("Scenario 1: TEST PASSED")
        except Exception as e:
            print(f"Scenario 1: TEST FAILED - {e}")
            await page.screenshot(path="scenario1_fail.png")
            # If scenario 1 fails, ensure we navigate back for the next test
            await page.goto(URL) # Ensure we are on the login page for the next scenario


        # --- Scenario 2: Verify Negative Login with Invalid Credentials ---
        print("\nRunning Scenario 2: Verify Negative Login with Invalid Credentials...")
        try:
            # Ensure we are on the login page before starting this scenario
            if page.url != URL:
                await page.goto(URL)

            await page.fill('#username', 'wronguser')
            await page.fill('#password', 'wrongpass')
            await page.click('#submit')

            # Expect to remain on the login page (URL does not change)
            await expect(page).to_have_url(URL)
            
            # Expect error message to be displayed and have specific text
            # Based on the provided DOM, the error message is in a div with id="error".
            # The DOM snippet shows 'Your username is invalid!' for the error div.
            error_message_locator = page.locator('#error')
            await expect(error_message_locator).to_be_visible()
            await expect(error_message_locator).to_have_text('Your username is invalid!')
            print("Scenario 2: TEST PASSED")
        except Exception as e:
            print(f"Scenario 2: TEST FAILED - {e}")
            await page.screenshot(path="scenario2_fail.png")


        # --- Scenario 3: Verify UI Element Functionality and Navigation ---
        print("\nRunning Scenario 3: Verify UI Element Functionality and Navigation...")
        try:
            # Ensure we are on the login page before starting this scenario
            if page.url != URL:
                await page.goto(URL)

            toggle_button = page.locator('#toggle-navigation')
            # The primary menu items are within a UL with id="menu-primary-items"
            menu_items_container = page.locator('#menu-primary-items')

            # 1. Click toggle button and verify menu becomes visible
            await toggle_button.click()
            await expect(menu_items_container).to_be_visible()
            print("   - Menu visible after first toggle click: PASSED")

            # 2. Click toggle button again and verify menu becomes hidden
            await toggle_button.click()
            await expect(menu_items_container).not_to_be_visible()
            print("   - Menu hidden after second toggle click: PASSED")

            # 3. Click the "Practice" navigation link
            # Need to make the menu visible again to click the link
            await toggle_button.click() # Re-open the menu
            await page.click('#menu-item-20 a') # Click the 'Practice' link using its ID and descendant 'a'

            # Expect navigation to the "Practice" page
            await expect(page).to_have_url("https://practicetestautomation.com/practice/")
            print("   - Navigated to Practice page: PASSED")

            print("Scenario 3: TEST PASSED")
        except Exception as e:
            print(f"Scenario 3: TEST FAILED - {e}")
            await page.screenshot(path="scenario3_fail.png")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())