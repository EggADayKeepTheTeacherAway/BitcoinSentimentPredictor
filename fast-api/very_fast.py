import sys
import os
import datetime
import requests
import tempfile

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
import praw
import nltk

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from prototype_data.predict import preprocess_reddit_data, predict_next_day, export_preprocessed_data, export_reddit_data, export_bitcoin_data
from tensorflow.keras.models import load_model
import pandas as pd
import joblib

load_dotenv()

app = FastAPI()

prototype_directory = os.path.abspath('../prototype_data')  # Adjust the relative path

# Add the directory to sys.path
sys.path.append(prototype_directory)

model_path = os.path.join(prototype_directory, 'btc_gru_model.h5')
scaler_path = os.path.join(prototype_directory, 'feature_scaler.pkl')

# Load the model and scaler
loaded_model = load_model(model_path)
loaded_scaler = joblib.load(scaler_path)

# Define a directory for exports if needed, or use tempfile
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

@app.get("/result")
async def get_predict_result():
    """
    Get the model result using dynamically fetched data.
    """
    print("Starting prediction process with dynamic data...")
    
    reddit_data = await get_reddit_post(limit=200)
    bitcoin_data = await get_bitcoin_price()
    
    new_market_data = preprocess_reddit_data(reddit_data, bitcoin_data)
    
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
      
@app.get("/download-preprocess-data")
async def download_preprocessed_data_endpoint():
    """
    Preprocesses the latest Reddit and Bitcoin data and returns it as a downloadable CSV file.
    """
    print("Starting data preprocessing for download...")
    try:
        # Reduce the limit significantly to speed up the process
        reddit_data = await get_reddit_post(limit=985)  # Reduced limit from 985
        bitcoin_data = await get_bitcoin_price()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w') as temp_file:
            output_filepath = temp_file.name

        print(f"Exporting preprocessed data to temporary file: {output_filepath}")

        export_preprocessed_data(reddit_data, bitcoin_data, output_filepath)

        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
             print(f"Export failed or file is empty: {output_filepath}")
             raise HTTPException(status_code=500, detail="Failed to generate preprocessed data file.")

        return FileResponse(
            path=output_filepath,
            filename=f"preprocessed_bitcoin_sentiment_{datetime.date.today()}.csv",
            media_type='text/csv',
        )

    except ValueError as ve:
        print(f"Preprocessing error: {ve}")
        raise HTTPException(status_code=400, detail=f"Data preprocessing error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'output_filepath' in locals() and os.path.exists(output_filepath):
             os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

# --- New Download Endpoints ---

@app.get("/download-reddit-data")
async def download_reddit_data_endpoint():
    """
    Preprocesses the latest Reddit data (sentiment, aggregation) and returns it as a downloadable CSV file.
    """
    print("Starting Reddit data preprocessing for download...")
    try:
        # Fetch raw Reddit data (adjust limit as needed for performance)
        reddit_data = await get_reddit_post(limit=200) 

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w') as temp_file:
            output_filepath = temp_file.name

        print(f"Exporting aggregated Reddit data to temporary file: {output_filepath}")

        # Call the specific export function for Reddit data
        recent_dates = export_reddit_data(reddit_data, output_filepath)

        if recent_dates is None or not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
             print(f"Reddit data export failed or file is empty: {output_filepath}")
             # Clean up if file exists but is empty/invalid
             if os.path.exists(output_filepath): os.remove(output_filepath)
             raise HTTPException(status_code=500, detail="Failed to generate aggregated Reddit data file.")

        return FileResponse(
            path=output_filepath,
            filename=f"aggregated_reddit_sentiment_{datetime.date.today()}.csv",
            media_type='text/csv',
        )

    except ValueError as ve:
        print(f"Reddit preprocessing error: {ve}")
        # Clean up temp file on error
        if 'output_filepath' in locals() and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=400, detail=f"Data preprocessing error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during Reddit data download: {e}")
        if 'output_filepath' in locals() and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")


@app.get("/download-bitcoin-price")
async def download_bitcoin_price_endpoint():
    """
    Fetches the latest Bitcoin price data and returns it as a downloadable CSV file.
    """
    print("Starting Bitcoin price data fetch for download...")
    try:
        bitcoin_data_list = await get_bitcoin_price()

        if not bitcoin_data_list:
            raise HTTPException(status_code=404, detail="No Bitcoin price data found.")
        
        bitcoin_df = pd.DataFrame(bitcoin_data_list)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w', encoding='utf-8') as temp_file:
            output_filepath = temp_file.name
            bitcoin_df.to_csv(output_filepath, index=False, encoding='utf-8')

        print(f"Bitcoin price data exported to temporary file: {output_filepath}")

        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
             print(f"Export failed or file is empty: {output_filepath}")
             if os.path.exists(output_filepath):
                 os.remove(output_filepath)
             raise HTTPException(status_code=500, detail="Failed to generate Bitcoin price data file.")
        return FileResponse(
            path=output_filepath,
            filename=f"bitcoin_price_last_30_days_{datetime.date.today()}.csv",
            media_type='text/csv',
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"An unexpected error occurred during Bitcoin price download: {e}")
        if 'output_filepath' in locals() and os.path.exists(output_filepath):
             os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

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