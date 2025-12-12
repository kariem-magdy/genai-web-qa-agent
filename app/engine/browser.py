import asyncio
from playwright.async_api import async_playwright
from config import Config

class BrowserManager:
    """
    Manages the Playwright browser instance.
    """
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            # Headless=False is critical for the "Visual Context" requirement
            self.browser = await self.playwright.chromium.launch(
                headless=Config.HEADLESS, 
                args=["--start-maximized"]
            )
            self.context = await self.browser.new_context(no_viewport=True)
            self.page = await self.context.new_page()

    async def navigate(self, url: str):
        if not self.page:
            await self.start()
        try:
            await self.page.goto(url, timeout=Config.TIMEOUT)
            await self.page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(2) # Brief wait for visual confirmation
        except Exception as e:
            return f"Error navigating: {str(e)}"

    async def get_content(self):
        if self.page:
            return await self.page.content()
        return ""

    async def take_screenshot(self, path="screenshot.png"):
        if self.page:
            await self.page.screenshot(path=path)
            return path
        return None

    async def execute_generated_test(self, code: str):
        """
        Executes generated Python code in a subprocess.
        """
        filename = "generated_test_runner.py"
        
        # Write code to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
            
        # Run in a separate process to ensure isolation
        proc = await asyncio.create_subprocess_exec(
            "python", filename,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await proc.communicate()
        
        output = ""
        if stdout: output += stdout.decode()
        if stderr: output += "\nERROR:\n" + stderr.decode()
        
        return output

    async def close(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()