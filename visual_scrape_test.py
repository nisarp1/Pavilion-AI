
import asyncio
from playwright.async_api import async_playwright
import google.generativeai as genai
import os
import json

def get_screenshot_analysis():
    # Only runs if Playwright is available
    async def run():
        print("Launching headless browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            
            # 1. Google Trends Realtime
            url = "https://trends.google.com/trending?geo=IN&hl=en-US&category=17"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for content to load
            try:
                await page.wait_for_selector('div[class*="feed-item"]', timeout=5000)
            except:
                print("Selector timeout, taking screenshot anyway")
                
            screenshot_path = "google_trends_visual.png"
            await page.screenshot(path=screenshot_path, full_page=False)
            print(f"Screenshot saved to {screenshot_path}")
            
            # 2. Analyze with Gemini
            api_key = os.environ.get('GEMINI_API_KEY', '')
            if not api_key:
                print("Missing GEMINI_API_KEY")
                return

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            print("Sending image to Gemini for analysis...")
            
            # Load image
            with open(screenshot_path, "rb") as f:
                image_data = f.read()
                
            prompt = """
            Look at this screenshot of Google Trends for Sports in India.
            Extract the list of trending topics (names of teams, players, events) that you see in the list.
            Return ONLY a JSON list of strings, like ["Team A vs Team B", "Player Name"].
            Do not include extracting redundant text like "20K+ searches".
            """
            
            response = model.generate_content([
                {'mime_type': 'image/png', 'data': image_data},
                prompt
            ])
            
            print("\n--- GEMINI VISUAL ANALYSIS ---")
            print(response.text)
            
            await browser.close()

    asyncio.run(run())

if __name__ == "__main__":
    get_screenshot_analysis()
