import os
import pytest
import time
from datetime import datetime
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
    page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=60000)
    page.wait_for_selector("iframe[title='streamlit_navigation_bar.st_navbar']", timeout=60000)
    print("Page loaded successfully")


def test_bitcoin_dashboard_refresh(page: Page):
    """
    Test refresh behavior of Bitcoin dashboard by checking timestamp update after clicking refresh.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[1:][0].click()

    page.wait_for_selector(".hi-playwright", timeout=60000)
    page.wait_for_selector("div[data-testid='stCaptionContainer']", timeout=60000)

    caption_text = page.locator("div[data-testid='stCaptionContainer'] > p").inner_text()
    original_time_str = caption_text.split()[-1]
    original_time = datetime.strptime(original_time_str, "%H:%M:%S")

    page.locator("button[data-testid='stBaseButton-secondary']").click()
    time.sleep(3)

    caption_text_after = page.locator("div[data-testid='stCaptionContainer'] > p").inner_text()
    new_time_str = caption_text_after.split()[-1]
    new_time = datetime.strptime(new_time_str, "%H:%M:%S")

    print(original_time, new_time)

    delta_seconds = (new_time - original_time).total_seconds()
    print(f"Time diff: {delta_seconds} seconds")
    assert delta_seconds >= 1, f"Expected at least 1 seconds between timestamps, got {delta_seconds:.2f}"


def test_sentiment_positive_submit(page: Page):
    """
    Test submit behavior of Sentiment Analysis by checking that the result will be positive and will show to the user.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[2:][0].click()

    page.wait_for_selector("button", timeout=60000)

    page.get_by_label("Put your comment here:").fill('I love Bitcoin')

    page.locator("button[data-testid='stBaseButton-secondary']").all()[0].click()

    page.wait_for_selector(".green", timeout=60000)
    
    page.locator(".green").scroll_into_view_if_needed()

    time.sleep(2)

def test_sentiment_negative_submit(page: Page):
    """
    Test submit behavior of Sentiment Analysis by checking that the result will be negative and will show to the user.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[2:][0].click()

    page.wait_for_selector("button", timeout=60000)

    page.get_by_label("Put your comment here:").fill('I hate you')

    page.locator("button[data-testid='stBaseButton-secondary']").all()[0].click()

    page.wait_for_selector(".red", timeout=60000)

    page.locator(".red").scroll_into_view_if_needed()

    time.sleep(2)
    

def test_sentiment_neutral_submit(page: Page):
    """
    Test submit behavior of Sentiment Analysis by checking that the result will be neutral and will show to the user.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[2:][0].click()

    page.wait_for_selector("button", timeout=60000)
    
    page.get_by_label("Put your comment here:").fill('Banana')

    page.locator("button[data-testid='stBaseButton-secondary']").all()[0].click()

    page.wait_for_selector(".gray", timeout=60000)

    page.locator(".gray").scroll_into_view_if_needed()

    time.sleep(2)



def test_sentiment_next(page: Page):
    """
    Test next post button it should go to next post.
    """
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[2:][0].click()

    page.wait_for_selector("button", timeout=60000)

    title = page.locator(".stHeading").inner_text()

    page.locator("button[data-testid='stBaseButton-secondary']").all()[1].click()

    page.locator("button[data-testid='stBaseButton-secondary']").all()[1].click()

    time.sleep(2)

    next_title = page.locator(".stHeading").inner_text()

    assert title != next_title


def test_api_excute_button(page: Page):
    wait_page_loading(page)

    navbar_iframe = page.frame_locator("iframe[title='streamlit_navigation_bar.st_navbar']")
    navbar_items = navbar_iframe.locator("li a, a.nav-link").all()
    navbar_items[3:][0].click()

    page.wait_for_selector(".stExpander", timeout=60000)

    dropdowns = page.locator(".stExpander").all()

    buttons = page.locator("button[data-testid='stBaseButton-secondary']").all()


    for i in range(len(dropdowns)):
        dropdowns[i].click()

        if i == 2:
            page.get_by_label("How many reddit posts (optional - uses API default if empty):").fill("2")
        
        elif i == 3:
            page.get_by_label("Text to analyze:").fill("I love you")

        buttons[i].click()
        
        page.wait_for_selector(".stJson", timeout=60000)

        time.sleep(3)


def test_whole_page(page: Page):
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
        
        page.wait_for_selector("div[data-testid='stAppViewContainer']", timeout=60000)
        page.wait_for_selector("iframe[title='streamlit_navigation_bar.st_navbar']", timeout=60000)

        if text == "Bitcoin":
            page.locator("button[data-testid='stBaseButton-secondary']").click()


        elif text == "Sentiment Analysis":
            page.get_by_label("Put your comment here:").fill('I love Bitcoin')

            page.locator("button[data-testid='stBaseButton-secondary']").all()[0].click()
            
            page.wait_for_selector(".green", timeout=60000)

            page.locator(".green").scroll_into_view_if_needed()

        elif text == "API":
            page.wait_for_selector(".stExpander", timeout=60000)

            dropdowns = page.locator(".stExpander").all()

            buttons = page.locator("button[data-testid='stBaseButton-secondary']").all()


            for i in range(len(dropdowns)):
                dropdowns[i].click()

                if i == 2:
                    page.get_by_label("How many reddit posts (optional - uses API default if empty):").fill("2")
                
                elif i == 3:
                    page.get_by_label("Text to analyze:").fill("I love you")

                buttons[i].click()
                
                page.wait_for_selector(".stJson", timeout=60000)

                time.sleep(3)

        time.sleep(5)

        page.screenshot(path=f"test/screenshots/nav_to_{text.lower().replace(' ', '_')}.png")


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
        page.set_default_timeout(60000)

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
        page.set_default_timeout(60000)
        test_bitcoin_dashboard_refresh(page)
        page.close()
        context.close()
        browser.close()
