import numpy as np
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

sid = SentimentIntensityAnalyzer()

def get_sentiment_local(text):
    """Optimized sentiment analysis function"""
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    return 'positive' if compound > 0.05 else 'negative' if compound < -0.05 else 'neutral'

def preprocess_bitcoin_data(bitcoin_data, recent_dates=None):
    """
    Preprocesses Bitcoin price data.
    - If recent_dates is provided, filters for those dates.
    - Calculates daily Open, Close, and Range for the available/filtered dates.
    """
    if isinstance(bitcoin_data, list):
        bitcoin_df = pd.DataFrame(bitcoin_data)
    else:
        bitcoin_df = bitcoin_data.copy()

    if 'date' not in bitcoin_df.columns:
        raise ValueError("Bitcoin data must contain a 'date' column.")
        
    try:
        bitcoin_df['Date'] = pd.to_datetime(bitcoin_df['date'], format='mixed').dt.date
    except Exception as e:
        raise ValueError(f"Error converting bitcoin 'date' column to datetime: {e}")

    if recent_dates:
        bitcoin_df = bitcoin_df[bitcoin_df['Date'].isin(recent_dates)]
        if bitcoin_df.empty:
            raise ValueError("No Bitcoin data found for the required recent dates.")
    elif bitcoin_df.empty:
         raise ValueError("No Bitcoin data found.")

    if 'price' not in bitcoin_df.columns:
        raise ValueError("Bitcoin data must contain a 'price' column.")

    bitcoin_agg = bitcoin_df.groupby('Date').agg(
        Open=('price', 'first'),
        Close=('price', 'last')
    ).reset_index()
    
    if bitcoin_agg['Open'].isnull().any() or bitcoin_agg['Close'].isnull().any():
        print("Warning: NaN found in Open/Close aggregation. Ensure sufficient price data per day.")
        bitcoin_agg['Close'] = bitcoin_agg['Close'].fillna(bitcoin_agg['Open'])

    bitcoin_agg['Range'] = bitcoin_agg['Close'] - bitcoin_agg['Open']
    
    return bitcoin_agg[['Date', 'Range', 'Open', 'Close']]

def preprocess_reddit_only(reddit_data, num_recent_dates=2):
    """
    Preprocesses only the Reddit data.
    - Calculates sentiment and aggregates metrics for the specified number of recent dates.
    - Returns aggregated data and the list of recent dates used.

    Args:
        reddit_data (list or pd.DataFrame): Raw Reddit data.
        num_recent_dates (int): The number of most recent dates to process. Defaults to 2.

    Returns:
        tuple: (pd.DataFrame containing aggregated data, list of recent dates used)
               Returns (None, None) if processing fails due to insufficient data.
               Raises ValueError for other processing errors.
    """
    if isinstance(reddit_data, list):
        reddit_df = pd.DataFrame(reddit_data)
    else:
        reddit_df = reddit_data.copy()

    reddit_df.rename(columns={
        'time': 'Timestamp',
        'title': 'Title',
        'text': 'Text',
        'upvote': 'Score',
        'num_comments': 'Comments',
        'upvote_ratio': 'Upvote Ratio',
        'id': 'ID'
    }, inplace=True)

    if 'Timestamp' not in reddit_df.columns:
        raise ValueError("Reddit data must contain a 'Timestamp' or 'time' column.")
    try:
        reddit_df['Date'] = pd.to_datetime(reddit_df['Timestamp'], errors='coerce').dt.date
        reddit_df.dropna(subset=['Date'], inplace=True)
        if reddit_df.empty:
             raise ValueError("No valid dates found in Reddit data after conversion.")
    except Exception as e:
        raise ValueError(f"Error converting Reddit 'Timestamp' column to datetime: {e}")

    if reddit_df['Date'].nunique() < num_recent_dates:
         print(f"Warning: Insufficient Reddit data - need posts from at least {num_recent_dates} different dates. Found {reddit_df['Date'].nunique()}.")
         return None, None

    recent_dates = sorted(reddit_df['Date'].unique(), reverse=True)[:num_recent_dates]

    recent_data = reddit_df[reddit_df['Date'].isin(recent_dates)].copy()

    recent_data['Title'] = recent_data['Title'].fillna('')
    recent_data['Text'] = recent_data['Text'].fillna('')
    
    recent_data['Sentiment'] = recent_data.apply(
        lambda row: get_sentiment_local(f"{row['Title']} {row['Text']}"),
        axis=1
    )

    required_cols = ['Score', 'Comments', 'Upvote Ratio', 'ID', 'Sentiment']
    for col in required_cols:
        if col not in recent_data.columns:
            if col == 'Upvote Ratio':
                 recent_data[col] = recent_data[col].fillna(0.0)
            elif col in ['Score', 'Comments']:
                 recent_data[col] = recent_data[col].fillna(0)
            else:
                 raise ValueError(f"Missing required column for aggregation: {col}")

    agg_data = recent_data.groupby('Date').agg(
        total_score=('Score', 'sum'),
        total_comments=('Comments', 'sum'),
        average_upvote_ratio=('Upvote Ratio', 'mean'),
        total_posts=('ID', 'count'),
        percentage_negative=('Sentiment', lambda x: (x == 'negative').mean() * 100),
        percentage_neutral=('Sentiment', lambda x: (x == 'neutral').mean() * 100),
        percentage_positive=('Sentiment', lambda x: (x == 'positive').mean() * 100)
    ).reset_index()

    return agg_data, recent_dates


def preprocess_reddit_data(reddit_data, bitcoin_data):
    """
    Preprocess Reddit and Bitcoin data by calling helper functions and merging.
    - Accepts lists of dictionaries (not file paths)
    - Specifically requests 2 days of Reddit data for prediction compatibility.
    """
    try:
        agg_data, recent_dates = preprocess_reddit_only(reddit_data, num_recent_dates=2)
        if agg_data is None or recent_dates is None:
             raise ValueError("Insufficient Reddit data - need posts from at least 2 different dates.")
    except ValueError as e:
        raise ValueError(f"Error processing Reddit data: {e}")

    try:
        bitcoin_agg = preprocess_bitcoin_data(bitcoin_data, recent_dates)
    except ValueError as e:
         raise ValueError(f"Error processing Bitcoin data: {e}")
    
    merged_data = pd.merge(agg_data, bitcoin_agg[['Date', 'Range']], on='Date', how='inner')
    
    merged_data = merged_data.sort_values('Date', ascending=True)

    if len(merged_data) < 2:
        raise ValueError("Merge failed or insufficient overlapping data - need at least 2 days of complete data for both sources after merging.")

    print("Preprocessed Merged Data (last 2 days):")
    print(merged_data)
    return merged_data

def predict_next_day(new_data, model, scaler, time_steps=2, features=None):
    """Optimized prediction function"""
    if 'Date' in new_data.columns:
        new_data_for_prediction = new_data.drop(columns=['Date'])
    else:
        new_data_for_prediction = new_data.copy()

    if features:
        new_data_for_prediction = new_data_for_prediction[features]
    
    scaled_data = scaler.transform(new_data_for_prediction)
    
    if len(scaled_data) < time_steps:
        raise ValueError(f"Need at least {time_steps} days of data")
    
    input_data = np.array([scaled_data[-time_steps:]])
    probability = model.predict(input_data, verbose=0)[0][0]
    
    return ('up' if probability > 0.5 else 'down'), float(probability)

def export_preprocessed_data(reddit_data, bitcoin_data, output_filepath):
    """
    Preprocesses Reddit and Bitcoin data and exports the result to a CSV file.

    Args:
        reddit_data (list or pd.DataFrame): Raw Reddit data.
        bitcoin_data (list or pd.DataFrame): Raw Bitcoin price data.
        output_filepath (str): The path where the CSV file will be saved.
    """
    try:
        processed_data = preprocess_reddit_data(reddit_data, bitcoin_data)
        
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        processed_data.to_csv(output_filepath, index=False)
        print(f"Preprocessed data successfully exported to {output_filepath}")
    except ValueError as ve:
        print(f"Error during preprocessing: {ve}")
    except Exception as e:
        print(f"An error occurred during export: {e}")


def export_reddit_data(reddit_data, output_filepath, num_recent_dates=2):
    """
    Preprocesses only the Reddit data for a specified number of recent dates
    and exports the aggregated result to a CSV file.

    Args:
        reddit_data (list or pd.DataFrame): Raw Reddit data.
        output_filepath (str): The path where the CSV file will be saved.
        num_recent_dates (int): The number of most recent dates to process. Defaults to 2.

    Returns:
        list: The recent dates used for aggregation, or None if export fails.
    """
    try:
        agg_data, recent_dates = preprocess_reddit_only(reddit_data, num_recent_dates=num_recent_dates)
        
        if agg_data is None or recent_dates is None:
            print(f"Skipping export: Insufficient Reddit data for {num_recent_dates} dates.")
            return None

        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        agg_data.to_csv(output_filepath, index=False)
        print(f"Aggregated Reddit data ({len(recent_dates)} days) successfully exported to {output_filepath}")
        return recent_dates
    except ValueError as ve:
        print(f"Error during Reddit data preprocessing/export: {ve}")
        return None
    except Exception as e:
        print(f"An error occurred during Reddit data export: {e}")
        return None


def export_bitcoin_data(bitcoin_data, output_filepath, recent_dates=None):
    """
    Preprocesses Bitcoin data (optionally filtered by recent_dates) and exports the result.

    Args:
        bitcoin_data (list or pd.DataFrame): Raw Bitcoin price data.
        output_filepath (str): The path where the CSV file will be saved.
        recent_dates (list, optional): List of the 2 recent dates (datetime.date objects) to filter by. Defaults to None (process all data).
    """
    try:
        bitcoin_agg = preprocess_bitcoin_data(bitcoin_data, recent_dates=recent_dates) 
        
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        bitcoin_agg.to_csv(output_filepath, index=False)
        print(f"Aggregated Bitcoin data successfully exported to {output_filepath}")
    except ValueError as ve:
        print(f"Error during Bitcoin data preprocessing/export: {ve}")
    except Exception as e:
        print(f"An error occurred during Bitcoin data export: {e}")

