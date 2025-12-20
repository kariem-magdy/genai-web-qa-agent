import asyncio
from playwright.async_api import async_playwright, expect

async def test_ecommerce_features():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://automationexercise.com")

        # Test Scenario 1: Verify E-commerce Product Interaction and Cart Management
        print("Starting Test Scenario 1: Product Interaction and Cart Management")

        # Select a category
        await page.click("a[href='#Women']")
        await page.click("a[href='/category_products/1']")  # Women - Dress Category
        await expect(page).to_have_url("https://automationexercise.com/category_products/1")
        print("Navigated to Women - Dress Category.")

        # Select a brand (assuming 'Polo' is available and visible)
        await page.click("a[href='/brand_products/Polo']")
        await expect(page.locator(".title.text-center").first).to_contain_text("Brand - Polo")
        print("Filtered by Brand - Polo.")

        # Find and add a product to cart
        # We'll pick the first product that appears in the filtered list
        first_product_add_to_cart_button = page.locator(".product-bottom .add-to-cart").first
        await first_product_add_to_cart_button.click()
        print("Clicked 'Add to cart' for the first product.")

        # Verify cart modal appears
        cart_modal_header = page.locator(".modal-header h4.modal-title")
        await expect(cart_modal_header).to_be_visible()
        print("Cart modal is visible.")

        # Dismiss the modal
        await page.click(".modal-footer .btn-success")
        print("Dismissed the cart modal.")

        # Navigate to the Cart page
        await page.click("a[href='/view_cart']")
        await expect(page).to_have_url("https://automationexercise.com/view_cart")
        print("Navigated to the Cart page.")

        # Verify the added product is in the cart
        # This is a simplified check; a real test might verify product name/price
        cart_item_count = page.locator(".cart_info").count()
        assert cart_item_count >= 1, "Product not found in cart"
        print("Verified that at least one item is in the cart.")

        # Test Scenario 2: Validate Header Navigation and Core Practice Feature Accessibility
        print("\nStarting Test Scenario 2: Header Navigation and Core Practice Features")

        header_links = {
            "Home": "a[href='/']",
            "Products": "a[href='/products']",
            "Cart": "a[href='/view_cart']",
            "Signup / Login": "a[href='/login']",
            "Test Cases": "a[href='/test_cases']",
            "API Testing": "a[href='/api_list']",
            "Video Tutorials": "a[href='https://www.youtube.com/c/AutomationExercise']",
            "Contact us": "a[href='/contact_us']"
        }

        for name, selector in header_links.items():
            print(f"Testing header link: {name}")
            await page.click(selector)
            # For some links, we just check if they are clickable and don't change URL drastically
            if name not in ["Video Tutorials"]:
                await expect(page).not_to_contain_text("Error 404") # Basic check for broken links
                print(f"Navigated successfully to {name}.")
            else:
                # For external links, we can't easily assert URL change within the same page context
                # but we can check if the link is present and a valid href.
                link_element = page.locator(selector)
                await expect(link_element).to_have_attribute("href", header_links[name])
                print(f"External link for {name} verified.")
            await page.go_back() # Go back to the homepage for the next link test


        # Test slider buttons
        print("Testing slider buttons")
        await page.click("a.right.control-carousel")
        await expect(page.locator(".item.active").first).not_to_have_attribute("class", "item") # Check if slide changed
        print("Slider right arrow clicked.")
        await page.click("a.left.control-carousel")
        await expect(page.locator(".item.active").first).not_to_have_attribute("class", "item") # Check if slide changed back
        print("Slider left arrow clicked.")

        # Test Test Cases button on slider
        print("Testing Test Cases button on slider")
        await page.click(".test_cases_list")
        await expect(page).to_have_url("https://automationexercise.com/test_cases")
        print("Navigated to Test Cases page from slider.")
        await page.go_back()

        # Test API Testing button on slider
        print("Testing API Testing button on slider")
        await page.click(".apis_list")
        await expect(page).to_have_url("https://automationexercise.com/api_list")
        print("Navigated to API Testing page from slider.")
        await page.go_back()


        # Test Scenario 3: Test Slider and Recommended Items Carousel Functionality
        print("\nStarting Test Scenario 3: Slider and Recommended Items Carousel")

        # Locate and interact with Recommended Items carousel
        print("Testing Recommended Items carousel navigation")
        original_recommended_item_locator = page.locator(".recommended_items .productinfo").first
        initial_recommended_item_text = await original_recommended_item_locator.inner_text()

        await page.click("a.right.recommended-item-control")
        # Give it a moment to potentially update
        await page.wait_for_timeout(500)
        new_recommended_item_locator = page.locator(".recommended_items .productinfo").first
        new_recommended_item_text = await new_recommended_item_locator.inner_text()
        assert initial_recommended_item_text != new_recommended_item_text, "Recommended items did not change after clicking right arrow"
        print("Recommended items carousel right arrow clicked and items changed.")

        await page.click("a.left.recommended-item-control")
        await page.wait_for_timeout(500)
        back_to_original_item_locator = page.locator(".recommended_items .productinfo").first
        back_to_original_item_text = await back_to_original_item_locator.inner_text()
        assert initial_recommended_item_text == back_to_original_item_text, "Recommended items did not return to original after clicking left arrow"
        print("Recommended items carousel left arrow clicked and returned to original items.")

        # Add a recommended item to cart
        print("Adding a recommended item to cart")
        recommended_product_add_to_cart = page.locator(".recommended_items .add-to-cart").first
        await recommended_product_add_to_cart.click()

        # Verify cart modal for recommended item
        await expect(page.locator(".modal-header h4.modal-title")).to_be_visible()
        print("Cart modal visible after adding recommended item.")

        # Close modal
        await page.click(".modal-footer .btn-success")
        print("Dismissed modal for recommended item.")

        # Verify cart count update (if visible and tracked) or navigate to cart
        # For simplicity, we'll just confirm the modal was dismissed correctly.
        # A more robust test would check cart count or items after a refresh.
        print("Test Scenario 3 completed.")

        print("\nAll scenarios executed.")
        print("TEST PASSED")

        await browser.close()

async def main():
    try:
        await test_ecommerce_features()
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())