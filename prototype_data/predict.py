import numpy as np
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()

def get_sentiment_local(text):
    """Optimized sentiment analysis function"""
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    return 'positive' if compound > 0.05 else 'negative' if compound < -0.05 else 'neutral'

def preprocess_reddit_data(file_path, bitcoin_prices_path):
    """
    Optimized preprocessing that:
    1. First filters to only recent dates needed
    2. Then processes sentiment and aggregates
    """
    reddit_data = pd.read_csv(file_path, usecols=[
        'Timestamp', 'Title', 'Text', 'Score', 'Comments', 'Upvote Ratio', 'ID'
    ])
    
    reddit_data['Date'] = pd.to_datetime(reddit_data['Timestamp']).dt.date
    recent_dates = sorted(reddit_data['Date'].unique(), reverse=True)[:2]
    # print(f"Recent dates found: {recent_dates}")
    
    recent_data = reddit_data[reddit_data['Date'].isin(recent_dates)].copy()
    
    recent_data['Sentiment'] = recent_data.apply(
        lambda row: get_sentiment_local(f"{row['Title']} {row['Text']}"), 
        axis=1
    )
    
    agg_data = recent_data.groupby('Date').agg(
        total_score=('Score', 'sum'),
        total_comments=('Comments', 'sum'),
        average_upvote_ratio=('Upvote Ratio', 'mean'),
        total_posts=('ID', 'count'),
        percentage_negative=('Sentiment', lambda x: (x == 'negative').mean() * 100),
        percentage_neutral=('Sentiment', lambda x: (x == 'neutral').mean() * 100),
        percentage_positive=('Sentiment', lambda x: (x == 'positive').mean() * 100)
    ).reset_index()
    
    bitcoin_df = pd.read_csv(bitcoin_prices_path)
    bitcoin_df['Date'] = pd.to_datetime(bitcoin_df['Date'], format='mixed').dt.date
    bitcoin_df = bitcoin_df[bitcoin_df['Date'].isin(recent_dates)]
    
    bitcoin_agg = bitcoin_df.groupby('Date').agg(
        Open=('Price (USD)', 'first'),
        Close=('Price (USD)', 'last')
    ).reset_index()
    bitcoin_agg['Range'] = bitcoin_agg['Close'] - bitcoin_agg['Open']
    
    merged_data = pd.merge(agg_data, bitcoin_agg[['Date', 'Range']], on='Date', how='inner')
    merged_data = merged_data.sort_values('Date', ascending=False).head(2)
    
    if len(merged_data) < 2:
        raise ValueError("Insufficient data - need at least 2 days of complete data")
    
    return merged_data.drop(columns=['Date'])

def predict_next_day(new_data, model, scaler, time_steps=2, features=None):
    """Optimized prediction function"""
    if features:
        new_data = new_data[features]
    
    scaled_data = scaler.transform(new_data)
    
    if len(scaled_data) < time_steps:
        raise ValueError(f"Need at least {time_steps} days of data")
    
    input_data = np.array([scaled_data[-time_steps:]])
    probability = model.predict(input_data, verbose=0)[0][0]
    
    return ('up' if probability > 0.5 else 'down'), float(probability)

