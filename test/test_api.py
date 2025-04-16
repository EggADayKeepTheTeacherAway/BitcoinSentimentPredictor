import re
import pytest
import requests

from datetime import datetime
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:6969"


@pytest.fixture(scope="module")
def bitcoin_api_data():
    response = requests.get(f"{BASE_URL}/bitcoin")
    assert response.status_code == 200
    return response.json()


def test_bitcoin_api_returns_list(bitcoin_api_data):
    assert isinstance(bitcoin_api_data, list), "Response should be a list"


def test_bitcoin_api_item_format(bitcoin_api_data):
   for item in bitcoin_api_data:
        assert "date" in item
        assert "price" in item
        try:
            datetime.strptime(item["date"], "%Y-%m-%d %H:%M")
        except ValueError:
            assert False, f"Invalid date format: {item['date']}"
        assert isinstance(item["price"], (float, int)), "Price should be a number"


@pytest.fixture(scope="module")
def reddit_api_data():
    response = requests.get(f"{BASE_URL}/reddit?limit=5")
    assert response.status_code == 200
    return response.json()


def test_reddit_api_returns_list(reddit_api_data):
    assert isinstance(reddit_api_data, list), "Response should be a list"


def test_reddit_api_item_format(reddit_api_data):
    data = reddit_api_data

    for item in data:
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
        assert isinstance(item["upvote"], (float, int)), "Upvote should be a number"
        assert isinstance(item["num_comments"], (float, int)), "Num_comments should be a number"
        assert isinstance(item["upvote_ratio"], (float, int)), "Upvote_ratio should be a number"

        assert isinstance(item["id"], str), "id should be a str"
        assert isinstance(item["url"], str), "url should be a str"
        assert isinstance(item["title"], str), "title should be a str"
        assert isinstance(item["text"], str), "text should be a str"


def test_reddit_api_length(reddit_api_data):
    assert len(reddit_api_data) == 5


def test_reddit_api_length_default():
    response = requests.get(f"{BASE_URL}/reddit")
    assert response.status_code == 200
    assert len(response.json()) == 985


def test_sentiment_api_status():
    response = requests.get(f"{BASE_URL}/sentiment?text=Omega")
    assert response.status_code == 200


def test_sentiment_api_type():
    response = requests.get(f"{BASE_URL}/sentiment?text=Bitcoin%20is%20going%20to%20the%20moon!")
    assert response.status_code == 200
    assert isinstance(response.json(), dict), "Response should be a JSON"


def test_sentiment_api_item_format():
    response = requests.get(f"{BASE_URL}/sentiment?text=Bitcoin%20is%20going%20to%20the%20moon!")
    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert "score" in data
    
    assert isinstance(data["result"], str), "result should be a str"
    assert isinstance(data["score"], dict), "score should be a JSON"
    
    data_field = [key for key in data['score'].keys()]
    assert "neg" in data_field
    assert "neu" in data_field
    assert "pos" in data_field
    assert "compound" in data_field

    assert isinstance(data['score']["neg"], (int, float)), "neg should be a number"
    assert isinstance(data['score']["neu"], (int, float)), "neu should be a number"
    assert isinstance(data['score']["pos"], (int, float)), "pos should be a number"
    assert isinstance(data['score']["compound"], (int, float)), "compound should be a number"
