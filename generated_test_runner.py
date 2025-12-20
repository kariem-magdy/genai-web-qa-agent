import asyncio
from playwright.async_api import async_playwright, expect

async def test_navigation_qa_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com")

        # Test Case 1: Verify Navigation and QA Links
        print("--- Testing Scenario 1: Verify Navigation and QA Links ---")
        try:
            # Header Navigation Links
            await page.click("a[href='/']")
            await expect(page).to_have_url("https://automationexercise.com/")
            print("  - Home link works.")

            await page.click("a[href='/products']")
            await expect(page).to_have_url("https://automationexercise.com/products")
            print("  - Products link works.")

            await page.click("a[href='/view_cart']")
            await expect(page).to_have_url("https://automationexercise.com/view_cart")
            print("  - Cart link works.")

            await page.click("a[href='/login']")
            await expect(page).to_have_url("https://automationexercise.com/login")
            print("  - Signup / Login link works.")

            await page.click("a[href='/test_cases']")
            await expect(page).to_have_url("https://automationexercise.com/test_cases")
            print("  - Test Cases (Header) link works.")

            await page.click("a[href='/api_list']")
            await expect(page).to_have_url("https://automationexercise.com/api_list")
            print("  - API Testing (Header) link works.")

            # YouTube link might open in a new tab, so we'll just check if it's clickable and present
            youtube_link = page.locator("a[href='https://www.youtube.com/c/AutomationExercise']")
            await expect(youtube_link).to_be_visible()
            print("  - Video Tutorials link is visible.")

            await page.click("a[href='/contact_us']")
            await expect(page).to_have_url("https://automationexercise.com/contact_us")
            print("  - Contact us link works.")

            # Slider Buttons/Links
            # Clicking Test Cases button in slider
            await page.click("a.test_cases_list")
            await expect(page).to_have_url("https://automationexercise.com/test_cases")
            print("  - Test Cases button in slider works.")

            # Clicking APIs list for practice button in slider
            await page.click("a.apis_list")
            await expect(page).to_have_url("https://automationexercise.com/api_list")
            print("  - APIs list for practice button in slider works.")

            print("Scenario 1 PASSED")
        except Exception as e:
            print(f"Scenario 1 FAILED: {e}")
        finally:
            await browser.close()

async def test_product_browsing_cart_addition():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com")

        # Test Case 2: Verify Product Browsing and Cart Addition
        print("\n--- Testing Scenario 2: Verify Product Browsing and Cart Addition ---")
        try:
            # Add a product from "Features Items"
            first_product_add_to_cart = page.locator(".features_items .col-sm-4").first.locator("a.btn.btn-default.add-to-cart")
            await first_product_add_to_cart.click()
            print("  - Clicked 'Add to cart' for the first feature item.")

            # Verify the cart modal appears
            cart_modal_title = page.locator("#cartModal .modal-title")
            await expect(cart_modal_title).to_be_visible()
            await expect(cart_modal_title).to_contain_text("Added!")
            print("  - Cart modal appeared correctly.")

            # Click "Continue Shopping" in the modal
            await page.click("#cartModal button.close-modal")
            await expect(cart_modal_title).not_to_be_visible()
            print("  - Clicked 'Continue Shopping' and modal closed.")

            # Add another product and this time click "View Cart"
            await page.click(first_product_add_to_cart) # Add it again to trigger the modal
            print("  - Clicked 'Add to cart' again for the first feature item.")
            await expect(cart_modal_title).to_be_visible()

            await page.click("#cartModal a[href='/view_cart']")
            await expect(page).to_have_url("https://automationexercise.com/view_cart")
            print("  - Clicked 'View Cart' and navigated to the cart page.")

            # Go back to the homepage to test recommended items
            await page.goto("https://automationexercise.com")

            # Add a product from "Recommended Items" (if visible, might need scrolling)
            # This requires a more robust way to ensure the element is visible and interactive.
            # For simplicity, we'll assume the first recommended item is visible for now.
            # A more robust approach would involve scrolling into view or waiting for it.
            recommended_product_add_to_cart = page.locator(".recommended_items .col-sm-4").first.locator("a.btn.btn-default.add-to-cart")
            await recommended_product_add_to_cart.click()
            print("  - Clicked 'Add to cart' for the first recommended item.")

            # Verify the cart modal appears again
            await expect(cart_modal_title).to_be_visible()
            print("  - Cart modal appeared correctly after adding from recommended items.")

            # Click "View Cart" from the modal
            await page.click("#cartModal a[href='/view_cart']")
            await expect(page).to_have_url("https://automationexercise.com/view_cart")
            print("  - Clicked 'View Cart' from recommended item modal and navigated to cart page.")


            print("Scenario 2 PASSED")
        except Exception as e:
            print(f"Scenario 2 FAILED: {e}")
        finally:
            await browser.close()

async def test_category_brand_filtering():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com")

        # Test Case 3: Verify Category and Brand Filtering
        print("\n--- Testing Scenario 3: Verify Category and Brand Filtering ---")
        try:
            # Test Category Filtering
            await page.click("#Women > span > i") # Expand Women category
            await page.click("a[href='/category_products/1']") # Click on Dress under Women
            await expect(page).to_have_url("https://automationexercise.com/category_products/1")
            # We can't directly verify if only dresses are shown without more complex selectors or page content analysis.
            # For now, we'll assume navigation is the primary check.
            print("  - Category Filtering: Navigated to Women > Dress.")

            await page.goto("https://automationexercise.com") # Go back to home for next test
            await page.click("#Men > span > i") # Expand Men category
            await page.click("a[href='/category_products/3']") # Click on Tshirts under Men
            await expect(page).to_have_url("https://automationexercise.com/category_products/3")
            print("  - Category Filtering: Navigated to Men > Tshirts.")

            await page.goto("https://automationexercise.com") # Go back to home for next test
            await page.click("#Kids > span > i") # Expand Kids category
            await page.click("a[href='/category_products/5']") # Click on Tops & Shirts under Kids
            await expect(page).to_have_url("https://automationexercise.com/category_products/5")
            print("  - Category Filtering: Navigated to Kids > Tops & Shirts.")


            # Test Brand Filtering
            await page.goto("https://automationexercise.com") # Ensure we are on the main page

            # Click on a brand
            await page.click("a[href='/brand_products/Polo']")
            await expect(page).to_have_url("https://automationexercise.com/brand_products/Polo")
            # Similar to category, verifying exact product listing requires more analysis.
            print("  - Brand Filtering: Navigated to Polo brand products.")

            await page.goto("https://automationexercise.com") # Go back to home for next test

            await page.click("a[href='/brand_products/H&M']")
            await expect(page).to_have_url("https://automationexercise.com/brand_products/H%26M") # Note the URL encoding
            print("  - Brand Filtering: Navigated to H&M brand products.")

            print("Scenario 3 PASSED")
        except Exception as e:
            print(f"Scenario 3 FAILED: {e}")
        finally:
            await browser.close()


async def main():
    await test_navigation_qa_links()
    await test_product_browsing_cart_addition()
    await test_category_brand_filtering()
    print("\n--- All Scenarios Executed ---")

if __name__ == "__main__":
    asyncio.run(main())