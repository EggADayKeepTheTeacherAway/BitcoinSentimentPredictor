import os
import pytest
import time
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import Page, expect, sync_playwright

IS_DIRECT_RUN = __name__ == "__main__"


def wait_page_loading(page: Page):
    """
    Navigates to the local Streamlit app and waits for the UI to load.
    
    Args:
        page (Page): Playwright page object.
    """
    page.goto("http://localhost:8501", timeout=60000)
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
    page.wait_for_selector("iframe[title='streamlit_navigation_bar.st_navbar']", timeout=30000)
    print("Page loaded successfully")


def test_can_switch_navbar(page: Page):
    """
    Test navigation by clicking through each navbar item and taking a screenshot.
    """
    Path("test/screenshots").mkdir(parents=True, exist_ok=True)
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()

    print(f"Found {len(navbar_items)} navbar items")
    for idx, item in enumerate(navbar_items):
        text = item.inner_text()
        print(f"Clicking navbar item {idx + 1}: {text}")
        item.click()
        page.wait_for_load_state("networkidle", timeout=30000)
        page.screenshot(path=f"test/screenshots/nav_to_{text.lower().replace(' ', '_')}.png")
        page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=30000)
        time.sleep(2)


def test_bitcoin_dashboard_refresh(page: Page):
    """
    Test refresh behavior of Bitcoin dashboard by checking timestamp update after clicking refresh.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[1:][0].click()

    page.wait_for_selector(".hi-playwright", timeout=30000)
    page.wait_for_selector("div[data-testid='stCaptionContainer']", timeout=30000)

    caption_text = page.locator("div[data-testid='stCaptionContainer'] > p").inner_text()
    original_time_str = caption_text.split()[-1]
    original_time = datetime.strptime(original_time_str, "%H:%M:%S")

    time.sleep(3)
    page.locator("button[data-testid='stBaseButton-secondary']").click()
    time.sleep(3)

    caption_text_after = page.locator("div[data-testid='stCaptionContainer'] > p").inner_text()
    new_time_str = caption_text_after.split()[-1]
    new_time = datetime.strptime(new_time_str, "%H:%M:%S")

    print(original_time, new_time)

    delta_seconds = (new_time - original_time).total_seconds()
    print(f"Time diff: {delta_seconds} seconds")
    assert delta_seconds >= 3, f"Expected at least 3 seconds between timestamps, got {delta_seconds:.2f}"


@pytest.fixture(scope="function")
def page(request):
    """
    Fixture to launch and close Playwright browser with video recording (if run via pytest).
    
    Yields:
        Page: Playwright page instance.
    """
    test_name = request.node.name if not IS_DIRECT_RUN else "manual_run"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context_kwargs = {
            "java_script_enabled": True,
            "viewport": {"width": 1280, "height": 720}
        }

        if not IS_DIRECT_RUN:
            video_path = Path("test/videos") / test_name
            video_path.mkdir(parents=True, exist_ok=True)
            context_kwargs["record_video_dir"] = str(video_path)
            context_kwargs["record_video_size"] = {"width": 1280, "height": 720}

        context = browser.new_context(**context_kwargs)
        page = context.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(30000)

        yield page

        page.close()

        if not IS_DIRECT_RUN:
            video_files = list(Path(context_kwargs["record_video_dir"]).glob("*.webm"))
            if video_files:
                video_file = video_files[0]
                timestamp = time.strftime("%Y_%m_%d_%H-%M-%S")
                new_name = Path(context_kwargs["record_video_dir"]) / f"{test_name}_{timestamp}.webm"
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
