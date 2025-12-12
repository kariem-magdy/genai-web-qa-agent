import pytest
from app.engine.browser import BrowserManager

@pytest.mark.asyncio
async def test_browser_startup():
    browser = BrowserManager()
    await browser.start()
    assert browser.page is not None
    await browser.close()

@pytest.mark.asyncio
async def test_code_execution_container():
    browser = BrowserManager()
    code = "print('TEST PASSED')"
    output = await browser.execute_generated_test(code)
    assert "TEST PASSED" in output