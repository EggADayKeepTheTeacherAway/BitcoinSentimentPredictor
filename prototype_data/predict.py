import numpy as np
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os # Added import

sid = SentimentIntensityAnalyzer()

def get_sentiment_local(text):
    """Optimized sentiment analysis function"""
    scores = sid.polarity_scores(text)
    compound = scores['compound']
    return 'positive' if compound > 0.05 else 'negative' if compound < -0.05 else 'neutral'

def preprocess_reddit_data(reddit_data, bitcoin_data):
    """
    Preprocess Reddit and Bitcoin data for prediction.
    - Accepts lists of dictionaries (not file paths)
    """

    # Convert to DataFrame if needed
    if isinstance(reddit_data, list):
        reddit_df = pd.DataFrame(reddit_data)
    else:
        reddit_df = reddit_data.copy()

    if isinstance(bitcoin_data, list):
        bitcoin_df = pd.DataFrame(bitcoin_data)
    else:
        bitcoin_df = bitcoin_data.copy()

    # Standardize column names
    reddit_df.rename(columns={
        'time': 'Timestamp',
        'title': 'Title',
        'text': 'Text',
        'upvote': 'Score',
        'num_comments': 'Comments',
        'upvote_ratio': 'Upvote Ratio',
        'id': 'ID'
    }, inplace=True)

    reddit_df['Date'] = pd.to_datetime(reddit_df['Timestamp']).dt.date
    recent_dates = sorted(reddit_df['Date'].unique(), reverse=True)[:2]

    recent_data = reddit_df[reddit_df['Date'].isin(recent_dates)].copy()

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

    # Convert bitcoin_data timestamp to date and prepare
    bitcoin_df['Date'] = pd.to_datetime(bitcoin_df['date'], format='mixed').dt.date
    bitcoin_df = bitcoin_df[bitcoin_df['Date'].isin(recent_dates)]

    bitcoin_agg = bitcoin_df.groupby('Date').agg(
        Open=('price', 'first'),
        Close=('price', 'last')
    ).reset_index()
    bitcoin_agg['Range'] = bitcoin_agg['Close'] - bitcoin_agg['Open']

    merged_data = pd.merge(agg_data, bitcoin_agg[['Date', 'Range']], on='Date', how='inner')
    merged_data = merged_data.sort_values('Date', ascending=False).head(2)

    if len(merged_data) < 2:
        raise ValueError("Insufficient data - need at least 2 days of complete data")
    
    print(merged_data)
    # Return the full merged data before dropping 'Date' for export purposes
    return merged_data

def predict_next_day(new_data, model, scaler, time_steps=2, features=None):
    """Optimized prediction function"""
    # Drop 'Date' column here if it exists, as it's not needed for prediction
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
        
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        processed_data.to_csv(output_filepath, index=False)
        print(f"Preprocessed data successfully exported to {output_filepath}")
    except ValueError as ve:
        print(f"Error during preprocessing: {ve}")
    except Exception as e:
        print(f"An error occurred during export: {e}")

