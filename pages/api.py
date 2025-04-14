import pathlib
import streamlit as st
import requests
import json
import pandas as pd

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)

# API Base URL
BASE_URL = "http://127.0.0.1:6969"

st.html("""
<h1>Bitcoin Predictor API Documentation</h1>
<p class="intro-text">
    This documentation provides information about the available endpoints in the Bitcoin Predictor API.
    You can test each endpoint directly from this interface by clicking the 'Execute' button.
</p>
""")

api_container = st.container()

with api_container:
    # 1. Prediction Endpoint
    with st.expander("Get Prediction Result", expanded=False):
        st.html("""
        <div class="api-header">
            <span class="method-get">GET</span>
            <span class="endpoint">/result</span>
        </div>
        <h3>Description</h3>
        <p class="description-text">
            Returns the prediction direction and confidence level for Bitcoin price movement.
        </p>
        """)
        
        if st.button("Execute", key="execute_result"):
            with st.spinner("Fetching data..."):
                try:
                    response = requests.get(f"{BASE_URL}/result")
                    if response.status_code == 200:
                        data = response.json()
                        st.html("<h3>Response</h3>")
                        st.json(data)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
        
        st.html("""
        <h3>Example Response</h3>
        <div class="example-response">
        {
        "direction": "down",
        "confident": "70%"
        }
        </div>
        """)
    
    # 2. Bitcoin Price Endpoint
    with st.expander("Get Bitcoin Price", expanded=False):
        st.html("""
        <div class="api-header">
            <span class="method-get">GET</span>
            <span class="endpoint">/bitcoin</span>
        </div>
        <h3>Description</h3>
        <p class="description-text">
            Returns Bitcoin price data for the last 30 days from CoinGecko.
        </p>
        """)
        
        if st.button("Execute", key="execute_bitcoin"):
            with st.spinner("Fetching Bitcoin price data..."):
                try:
                    response = requests.get(f"{BASE_URL}/bitcoin")
                    if response.status_code == 200:
                        data = response.json()
                        st.html("<h3>Response</h3>")
                        
                        # Display JSON data with limit
                        if len(data) > 20:
                            st.json(data[:20])
                            st.info(f"Showing first 20 of {len(data)} records")
                        else:
                            st.json(data)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
        
        st.html("""
        <h3>Example Response</h3>
        <div class="example-response">
        [
        {
            "date": "2025-03-15 12:00",
            "price": 78453.21
        },
        {
            "date": "2025-03-15 13:00",
            "price": 78512.65
        }
        ]
        </div>
        """)
    
    # 3. Reddit Posts Endpoint
    with st.expander("Get Reddit Posts", expanded=False):
        st.html("""
        <div class="api-header">
            <span class="method-get">GET</span>
            <span class="endpoint">/reddit</span>
        </div>
        <h3>Description</h3>
        <p class="description-text">
            Returns recent posts from the Bitcoin subreddit.
        </p>
        """)
        
        if st.button("Execute", key="execute_reddit"):
            with st.spinner("Fetching Reddit posts data..."):
                try:
                    response = requests.get(f"{BASE_URL}/reddit")
                    if response.status_code == 200:
                        data = response.json()
                        st.html("<h3>Response</h3>")
                        
                        # Display JSON data with limit
                        if len(data) > 20:
                            st.json(data[:20])
                            st.info(f"Showing first 20 of {len(data)} records")
                        else:
                            st.json(data)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
        
        st.html("""
        <h3>Example Response</h3>
        <div class="example-response">
        [
        {
            "id": "abcd123",
            "time": "2025-04-13 14:23:45",
            "url": "https://www.reddit.com/r/Bitcoin/comments/abcd123/example_post",
            "title": "Example Bitcoin Post",
            "upvote": 42,
            "num_comments": 7,
            "text": "This is the content of the post.",
            "upvote_ratio": 0.95
        }
        ]
        </div>
        """)
    
    # 4. Sentiment Analysis Endpoint
    with st.expander("Get Sentiment Analysis", expanded=False):
        st.html("""
        <div class="api-header">
            <span class="method-get">GET</span>
            <span class="endpoint">/sentiment</span>
        </div>
        <h3>Description</h3>
        <p class="description-text">
            Analyzes the sentiment of provided text using NLTK's VADER sentiment analyzer.
        </p>
        <h3>Parameters</h3>
        <table class="parameters-table">
            <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Description</th>
                <th>Required</th>
            </tr>
            <tr>
                <td>text</td>
                <td>string</td>
                <td>The text to analyze</td>
                <td>Yes</td>
            </tr>
        </table>
        """)
        
        # Query parameter input
        text_param = st.text_input("Text to analyze:", key="sentiment_text_param")
        
        if st.button("Execute", key="execute_sentiment"):
            if not text_param:
                st.error("Text parameter is required")
            else:
                with st.spinner("Analyzing sentiment..."):
                    try:
                        response = requests.get(f"{BASE_URL}/sentiment", params={"text": text_param})
                        if response.status_code == 200:
                            data = response.json()
                            st.html("<h3>Response</h3>")
                            st.json(data)
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Error connecting to API: {str(e)}")
        
        st.html("""
        <h3>Example Response</h3>
        <div class="example-response">
        {
        "result": "positive",
        "score": {
            "neg": 0.0,
            "neu": 0.323,
            "pos": 0.677,
            "compound": 0.7906
        }
        }
        </div>
        """)


# Footer
st.html("""
<div class="footer">
    <h3>Using the API in your code</h3>
    <p>You can also use these API endpoints in your own applications. Here's an example using Python:</p>
</div>
""")

st.code("""
import requests

# Get prediction
response = requests.get("http://127.0.0.1:6969/result")
prediction = response.json()
print(f"Bitcoin prediction: {prediction['direction']} with {prediction['confident']} confidence")

# Analyze sentiment
text = "Bitcoin is going to the moon!"
response = requests.get("http://127.0.0.1:6969/sentiment", params={"text": text})
sentiment = response.json()
print(f"Sentiment: {sentiment['result']} (Score: {sentiment['score']['compound']})")
""", language="python")