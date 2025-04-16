import os
import pytest
import time
import inspect
from playwright.sync_api import Page, expect, sync_playwright
from pathlib import Path


def test_can_switch_navbar(page: Page):
    page.goto("http://localhost:8501", timeout=60000)  
    
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
    
    page.wait_for_selector("iframe[title='streamlit_navigation_bar.st_navbar']", timeout=30000)
    
    Path("test/screenshots").mkdir(parents=True, exist_ok=True)

    print("Page loaded successfully")    
    
    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    
    # Process navbar items if found
    print(f"Found {len(navbar_items)} navbar items")
    for idx, item in enumerate(navbar_items):
        text = item.inner_text()
        print(f"Clicking navbar item {idx + 1}: {text}")
        
        item.click()
        
        page.wait_for_load_state("networkidle", timeout=30000)
        
        page.screenshot(path=f"test/screenshots/nav_to_{text.lower().replace(' ', '_')}.png")
        
        # Wait for app container to confirm page loaded
        page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)

        time.sleep(2)


def test_bitcoin_dashboard_refresh(page: Page):
    page.goto("https://www.youtube.com/watch?v=2KuWjZD6PBA&list=RD6YbqME4xI00&index=12", timeout=60000)  



@pytest.fixture(scope="function")
def page(request):
    test_name = request.node.name

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        videos_dir = Path("test/videos")
        videos_dir.mkdir(parents=True, exist_ok=True)

        video_path = videos_dir / test_name
        video_path.mkdir(parents=True, exist_ok=True)

        context = browser.new_context(
            record_video_dir=video_path,
            record_video_size={"width": 1280, "height": 720},
            java_script_enabled=True
        )
        page = context.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(30000)

        yield page

        page.close()

        video_files = list(video_path.glob("*.webm"))
        if video_files:
            video_file = video_files[0]

            # Get current timestamp
            timestamp = time.strftime("%Y_%m_%d_%H-%M-%S")  # e.g., 20250413_153020

            # New filename with timestamp
            new_name = video_path / f"{test_name}_{timestamp}.webm"

            # Try renaming until file is released
            for i in range(10):
                try:
                    os.rename(video_file, new_name)
                    print(f"Renamed video to: {new_name}")
                    break
                except PermissionError:
                    print(f"Waiting for video to be released... attempt {i+1}")
                    time.sleep(0.5)
            else:
                print(f"Could not rename video: {video_file}")

        context.close()
        browser.close()