import re
import pytest
import requests

from datetime import datetime
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:6969"


# /bitcoin
@pytest.fixture(scope="module")
def bitcoin_api_data():
    """
    Fixture to fetch Bitcoin API data.

    Returns:
        list: Parsed JSON response from the /bitcoin endpoint.
    """
    response = requests.get(f"{BASE_URL}/bitcoin")
    assert response.status_code == 200
    return response.json()


def test_bitcoin_api_returns_list(bitcoin_api_data):
    """Test that the /bitcoin endpoint returns a list."""
    assert isinstance(bitcoin_api_data, list), "Response should be a list"


def test_bitcoin_api_item_format(bitcoin_api_data):
    """Test each item in /bitcoin has valid date and price fields."""
    for item in bitcoin_api_data:
        assert "date" in item
        assert "price" in item
        try:
            datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
        except ValueError:
            assert False, f"Invalid date format: {item['date']}"
        assert isinstance(item["price"], (float, int)), "Price should be a number"


# /reddit
@pytest.fixture(scope="module")
def reddit_api_data():
    """
    Fixture to fetch Reddit API data with limit=5.

    Returns:
        list: Parsed JSON response from the /reddit endpoint.
    """
    response = requests.get(f"{BASE_URL}/reddit?limit=5")
    assert response.status_code == 200
    return response.json()


def test_reddit_api_returns_list(reddit_api_data):
    """Test that the /reddit endpoint returns a list."""
    assert isinstance(reddit_api_data, list), "Response should be a list"


def test_reddit_api_item_format(reddit_api_data):
    """Test that each Reddit post contains valid fields and types."""
    for item in reddit_api_data:
        assert "id" in item
        assert "time" in item
        assert "url" in item
        assert "title" in item
        assert "upvote" in item
        assert "num_comments" in item
        assert "text" in item
        assert "upvote_ratio" in item
        try:
            datetime.strptime(item["time"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            assert False, f"Invalid date format: {item['time']}"
        assert isinstance(item["upvote"], (float, int))
        assert isinstance(item["num_comments"], (float, int))
        assert isinstance(item["upvote_ratio"], (float, int))
        assert isinstance(item["id"], str)
        assert isinstance(item["url"], str)
        assert isinstance(item["title"], str)
        assert isinstance(item["text"], str)


def test_reddit_api_length(reddit_api_data):
    """Test that Reddit API returns exactly 5 posts with limit=5."""
    assert len(reddit_api_data) == 5


def test_reddit_api_length_default():
    """Test the default length of Reddit API response (More than 500 expected)."""
    response = requests.get(f"{BASE_URL}/reddit")
    assert response.status_code == 200
    assert len(response.json()) > 500


# /sentiment
def test_sentiment_api_status():
    """Test /sentiment endpoint returns HTTP 200."""
    response = requests.get(f"{BASE_URL}/sentiment?text=Omega")
    assert response.status_code == 200


def test_sentiment_api_type():
    """Test that /sentiment returns a dictionary."""
    response = requests.get(f"{BASE_URL}/sentiment?text=Bitcoin%20is%20going%20to%20the%20moon!")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_sentiment_api_item_format():
    """Test structure of sentiment API response."""
    response = requests.get(f"{BASE_URL}/sentiment?text=Bitcoin%20is%20going%20to%20the%20moon!")
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "score" in data
    assert isinstance(data["result"], str)
    assert isinstance(data["score"], dict)


def test_sentiment_api_score_item_format():
    """Test keys and types in 'score' of sentiment response."""
    response = requests.get(f"{BASE_URL}/sentiment?text=Bitcoin%20is%20going%20to%20the%20moon!")
    assert response.status_code == 200
    data = response.json()
    for field in ["neg", "neu", "pos", "compound"]:
        assert field in data["score"]
        assert isinstance(data["score"][field], (int, float))


# /result
def test_model_result_api_status():
    """Test that /result endpoint returns HTTP 200."""
    response = requests.get(f"{BASE_URL}/result")
    assert response.status_code == 200


def test_model_result_api_type():
    """Test that /result returns a dictionary."""
    response = requests.get(f"{BASE_URL}/result")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_model_result_api_item_format():
    """Test structure and data types of /result API response."""
    response = requests.get(f"{BASE_URL}/result")
    assert response.status_code == 200
    data = response.json()
    assert "direction" in data
    assert "confident" in data
    assert isinstance(data["direction"], str)
    assert isinstance(data["confident"], (float, int))
