import os
import datetime
import requests

import uvicorn
import praw
import nltk

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

load_dotenv()

app = FastAPI()

@app.get("/result")
async def get_predict_result():
    """
    Get the model result.
    """
    return {
        "direction": "down",
        "confident": "70%",
        }


@app.get("/bitcoin")
async def get_bitcoin_price():
    """
        Get the last 30 days of bitcoin price.
    """
    coin_id = "bitcoin"
    vs_currency = "usd"
    days = "30"  # gets the last 30 days of data.
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        prices = data["prices"]

        csv_data = [] 
        for timestamp, price in prices:
            date = datetime.datetime.fromtimestamp(timestamp / 1000, tz=datetime.timezone.utc)
            formatted_date = date.strftime("%Y-%m-%d %H:%M")
            csv_data.append({"date": formatted_date, "price": price})

    return csv_data


@app.get("/reddit")
async def get_reddit_post(limit: int = Query(985, description="Maximum number of posts to retrieve")):
    """
    Get the reddit post relate to bitcoin.
    """
    # Reddit API credentials
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")

    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    subreddit_name = "bitcoin"  # Change this to any subreddit
    num_posts = limit  # Target number of posts

    data = []
    count = 0

    # Fetch posts from the subreddit (newest first)
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.new(limit=None):  # limit=None fetches as many as possible
        if count >= num_posts:
            break  # Stop once we reach 10,000 posts

        data.append({
            "id": submission.id,
            "time": datetime.datetime.fromtimestamp(submission.created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            "url": submission.url,
            "title": submission.title,
            "upvote": submission.score,
            "num_comments": submission.num_comments,
            "text": submission.selftext,
            "upvote_ratio": submission.upvote_ratio if hasattr(submission, 'upvote_ratio') else None,
        })
        count += 1

    return data


@app.get("/sentiment")
async def get_sentiment(text: str = Query(..., description="The input text to analyze")):
    """
    Get the sentiment result and score.
    """
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    compound_score = scores['compound']
    result = ""
    if compound_score > 0.05:
        result = 'positive'
    elif compound_score < -0.05:
        result = 'negative'
    else:
        result = 'neutral'
    return {"result": result, "score": scores}

# uvicorn very_fast:app --port 6969 --reload

if __name__ == "__main__":
    uvicorn.run("very_fast:app", host="127.0.0.1", port=6969, reload=True)