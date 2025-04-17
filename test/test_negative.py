import pytest
import requests
import os
import time
from pathlib import Path
from playwright.sync_api import Page, sync_playwright


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


BASE_URL = "http://127.0.0.1:6969"


def test_sentiment_api_score_invalid_input():
    """Test result of sentiment API response."""
    response = requests.get(f"{BASE_URL}/sentiment")
    assert response.status_code == 422
  
    response = requests.get(f"{BASE_URL}/sentiment", params={"text": ""})
    assert response.status_code == 200
    assert response.json()["result"] == "neutral"


    response = requests.get(f"{BASE_URL}/sentiment", params={"text": "123456"})
    assert response.status_code == 200
    assert response.json()["result"] == "neutral"


def test_api_sentiment_excute_button_show_error(page: Page):
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[3:][0].click()

    page.wait_for_selector(".stExpander", timeout=30000)

    page.locator(".stExpander").all()[-1].click()

    page.locator("button[data-testid='stBaseButton-secondary']").all()[-1].click()

    page.wait_for_selector("div[data-testid='stAlertContentError']") # show error

    page.locator("div[data-testid='stAlertContentError']").scroll_into_view_if_needed()

    time.sleep(2)
  

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


if IS_DIRECT_RUN:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_navigation_timeout(60000)
        page.set_default_timeout(30000)
        test_api_excute_button(page)
        page.close()
        context.close()
        browser.close()
