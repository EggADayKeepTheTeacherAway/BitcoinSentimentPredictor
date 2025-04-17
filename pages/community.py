import random
import pathlib
import streamlit as st
import requests


def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)

# API Base URL
BASE_URL = "http://127.0.0.1:6969"


def get_reddit_data():
    try:
        response = requests.get(f"{BASE_URL}/reddit", params={"limit": 45})
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            st.error(f"Error fetching Reddit data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None


def analyze_sentiment(text):
    try:           
        response = requests.get(f"{BASE_URL}/sentiment", params={"text": text})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error analyzing sentiment: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to sentiment API: {str(e)}")
        return None


if "reddit_data" not in st.session_state:
    with st.spinner("Loading Reddit posts..."):
        st.session_state.reddit_data = get_reddit_data()


if "seen_posts" not in st.session_state:
    st.session_state.seen_posts = set()


if "current_post" not in st.session_state and st.session_state.reddit_data:
    # not seen before and have texttttttttttttt
    available_posts = [post for post in st.session_state.reddit_data 
                       if post["id"] not in st.session_state.seen_posts and post["text"]]
    
    if available_posts:

        reddit_post = random.choice(available_posts)
        st.session_state.current_post = reddit_post
        st.session_state.seen_posts.add(reddit_post["id"])
 
# enough with session let's do main thing here
if "current_post" in st.session_state and st.session_state.current_post:
    st.html("<h1 class='hero-animation'>Sentiment Analysis</h1>")

    st.info("Please click the button twice if it doesn't working.")

    st.header(st.session_state.current_post["title"])
    st.write(st.session_state.current_post["text"])
    
    st.divider()
    comment = st.text_input(label="Put your comment here:")
    
    col1, col2 = st.columns([1, 20])
    
    with col1:
        submit_button = st.button("Submit")
    
    with col2:
        next_post_button = st.button("Next Post")

    if submit_button and comment:
        sentiment_result = analyze_sentiment(comment)
        
        if sentiment_result:
            result = sentiment_result["result"]
            score = sentiment_result["score"]["compound"]
            
            result_color = {
                "positive": "green",
                "neutral": "gray",
                "negative": "red"
            }.get(result, "gray")
            
            st.html(f"""
            <div style="padding: 15px; border-radius: 5px; background-color: {result_color}20; margin-top: 10px;">
                <h4>Sentiment Analysis</h4>
                <p>Your comment has a <span class="{result_color}"; style="color: {result_color}; font-weight: bold;">{result}</span> sentiment.</p>
                <p>Sentiment score: {score:.3f}</p>
                <div style="display: flex; align-items: center; width: 100%; height: 15px; margin: 10px 0;">
                    <div style="width: 100%; height:15px; background-color: #f0f0f0; border-radius: 10px; position: relative;">

                        <div style="position: absolute; left: 50%; width: 2px; height: 100%; background-color: #aaa;"></div>
                        {
                        # For negative sentiment (left side)
                        f'<div style="position: absolute; right: 50%; width: {abs(score) * 50}%; height: 100%; background-color: #db4444; border-radius: 10px 0 0 10px;"></div>' 
                        if score < 0 else 
                        # For positive sentiment (right side)
                        f'<div style="position: absolute; left: 50%; width: {score * 50}%; height: 100%; background-color: #38ab38; border-radius: 0 10px 10px 0;"></div>'
                        if score > 0 else 
                        # For exactly zero
                        ''
                        }
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                    <span>Negative</span>
                    <span>Neutral</span>
                    <span>Positive</span>
                </div>
            </div>
            """)
    
    # Handle next post button
    if next_post_button:
        st.session_state.pop("current_post", None)


else:
    st.error("No Reddit posts with text content available.")
    if st.button("Reload posts"):
        st.session_state.reddit_data = get_reddit_data()
        st.session_state.seen_posts = set()
        st.session_state.pop("current_post", None)
