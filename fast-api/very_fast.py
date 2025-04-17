import sys
import os
import datetime
import requests

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
import praw
import nltk

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from prototype_data.predict import preprocess_reddit_data, predict_next_day
from tensorflow.keras.models import load_model
import joblib

nltk.download('vader_lexicon')

load_dotenv()

app = FastAPI()

prototype_directory = os.path.abspath('../prototype_data')  # Adjust the relative path

# Add the directory to sys.path
sys.path.append(prototype_directory)

model_path = os.path.join(prototype_directory, 'btc_gru_model.h5')
scaler_path = os.path.join(prototype_directory, 'feature_scaler.pkl')
market_data_path = os.path.join(prototype_directory, 'left_reddit_data.csv')
bitcoin_data_path = os.path.join(prototype_directory, 'bitcoin_prices.csv')

# Load the model and scaler
loaded_model = load_model(model_path)
loaded_scaler = joblib.load(scaler_path)

@app.get("/result")
async def get_predict_result():
    """
    Get the model result.
    """
    new_market_data = preprocess_reddit_data(market_data_path, bitcoin_data_path)
    prediction, confidence = predict_next_day(
        new_market_data,
        loaded_model,
        loaded_scaler,
        time_steps=2,
        features=['Range', 'total_score', 'total_comments', 'average_upvote_ratio',
                    'total_posts', 'percentage_negative',
                    'percentage_neutral', 'percentage_positive']
    )
    return {
        "direction": prediction,
        "confident": round(confidence * 100, 2),
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

    subreddit_name = "bitcoin"
    num_posts = limit  # Target number of posts

    data = []
    count = 0

    # Fetch posts from the subreddit (newest first)
    subreddit = reddit.subreddit(subreddit_name)

    for submission in subreddit.new(limit=None):  # limit=None fetches as many as possible
        if count >= num_posts:
            break

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