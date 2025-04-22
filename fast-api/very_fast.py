import sys
import os
import datetime
import requests
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uvicorn
import praw
import nltk

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from prototype_data.predict import preprocess_reddit_data, predict_next_day, export_preprocessed_data, export_reddit_data, export_bitcoin_data, preprocess_reddit_only
from tensorflow.keras.models import load_model
import pandas as pd
import joblib

load_dotenv()

app = FastAPI()

prototype_directory = os.path.abspath('../prototype_data')

sys.path.append(prototype_directory)

model_path = os.path.join(prototype_directory, 'btc_gru_model.h5')
scaler_path = os.path.join(prototype_directory, 'feature_scaler.pkl')

loaded_model = load_model(model_path)
loaded_scaler = joblib.load(scaler_path)

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

@app.get("/result")
async def get_predict_result():
    try:
        reddit_data = await get_reddit_post(limit=985)
        bitcoin_data = await get_bitcoin_price()
        new_market_data = preprocess_reddit_data(reddit_data, bitcoin_data)
        if new_market_data is None:
            raise HTTPException(status_code=400, detail="Data preprocessing failed, likely due to insufficient unique dates in Reddit data.")
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
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Prediction process error: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/download-preprocess-data")
async def download_preprocessed_data_endpoint():
    output_filepath = None
    try:
        reddit_data = await get_reddit_post(limit=985)
        bitcoin_data = await get_bitcoin_price()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w') as temp_file:
            output_filepath = temp_file.name
        export_preprocessed_data(reddit_data, bitcoin_data, output_filepath)
        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
             if output_filepath and os.path.exists(output_filepath):
                 os.remove(output_filepath)
             raise HTTPException(status_code=500, detail="Failed to generate preprocessed data file (possibly due to insufficient source data).")
        return FileResponse(
            path=output_filepath,
            filename=f"preprocessed_bitcoin_sentiment_{datetime.date.today()}.csv",
            media_type='text/csv',
        )
    except ValueError as ve:
        if output_filepath and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=400, detail=f"Data preprocessing/export error: {ve}")
    except Exception as e:
        if output_filepath and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/download-reddit-data")
async def download_reddit_data_endpoint():
    try:
        reddit_data_list = await get_reddit_post(limit=985) 
        if not reddit_data_list:
             raise HTTPException(status_code=404, detail="No Reddit posts found.")
        reddit_df = pd.DataFrame(reddit_data_list)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w', encoding='utf-8') as temp_file:
            output_filepath = temp_file.name
            reddit_df.to_csv(output_filepath, index=False, encoding='utf-8')
        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
             if os.path.exists(output_filepath): os.remove(output_filepath)
             raise HTTPException(status_code=500, detail="Failed to generate raw Reddit data file.")
        return FileResponse(
            path=output_filepath,
            filename=f"raw_reddit_posts_{datetime.date.today()}.csv",
            media_type='text/csv',
        )
    except ValueError as ve:
        if 'output_filepath' in locals() and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=400, detail=f"Data processing error: {ve}")
    except Exception as e:
        if 'output_filepath' in locals() and os.path.exists(output_filepath): os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/download-bitcoin-price")
async def download_bitcoin_price_endpoint():
    try:
        bitcoin_data_list = await get_bitcoin_price()
        if not bitcoin_data_list:
            raise HTTPException(status_code=404, detail="No Bitcoin price data found.")
        bitcoin_df = pd.DataFrame(bitcoin_data_list)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=EXPORT_DIR, mode='w', encoding='utf-8') as temp_file:
            output_filepath = temp_file.name
            bitcoin_df.to_csv(output_filepath, index=False, encoding='utf-8')
        if not os.path.exists(output_filepath) or os.path.getsize(output_filepath) == 0:
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
        if 'output_filepath' in locals() and os.path.exists(output_filepath):
             os.remove(output_filepath)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.get("/aggregated-reddit-data")
async def get_aggregated_reddit_data():
    try:
        reddit_data = await get_reddit_post(limit=985)
        result_data, _ = preprocess_reddit_only(reddit_data, 10)

        if isinstance(result_data, pd.DataFrame):
            return result_data.to_dict(orient='records')
        else:
            return []

    except ValueError as ve:
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal server error occurred processing aggregated data: {e}")

@app.get("/bitcoin")
async def get_bitcoin_price():
    coin_id = "bitcoin"
    vs_currency = "usd"
    days = "30"
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
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    USER_AGENT = os.getenv("USER_AGENT")
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    subreddit_name = "bitcoin"
    num_posts = limit
    data = []
    count = 0
    subreddit = reddit.subreddit(subreddit_name)
    for submission in subreddit.new(limit=None):
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

if __name__ == "__main__":
    uvicorn.run("very_fast:app", host="127.0.0.1", port=6969, reload=True)