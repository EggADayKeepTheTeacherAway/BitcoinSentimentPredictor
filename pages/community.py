import random
import pathlib
import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

def get_aggregated_reddit_data():
    """Fetches aggregated Reddit data from the API."""
    try:
        response = requests.get(f"{BASE_URL}/aggregated-reddit-data")
        if response.status_code == 200:
            data = response.json()
            if not data:
                 st.warning("Aggregated Reddit data endpoint returned empty data.")
                 return None
            df = pd.DataFrame(data)
            df['Date'] = pd.to_datetime(df['Date']) 
            return df
        else:
            st.error(f"Error fetching aggregated Reddit data: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to aggregated Reddit data API: {str(e)}")
        return None

if "reddit_data" not in st.session_state:
    with st.spinner("Loading Reddit posts..."):
        st.session_state.reddit_data = get_reddit_data()

if "seen_posts" not in st.session_state:
    st.session_state.seen_posts = set()

if "current_post" not in st.session_state and st.session_state.reddit_data:
    available_posts = [post for post in st.session_state.reddit_data 
                       if post["id"] not in st.session_state.seen_posts and post["text"]]
    
    if available_posts:
        reddit_post = random.choice(available_posts)
        st.session_state.current_post = reddit_post
        st.session_state.seen_posts.add(reddit_post["id"])

# Initialize session state for Reddit download data
if 'reddit_download_content' not in st.session_state:
    st.session_state.reddit_download_content = None
if 'reddit_download_filename' not in st.session_state:
    st.session_state.reddit_download_filename = None

# enough with session let's do main thing here
if "current_post" in st.session_state and st.session_state.current_post:
    st.html("<h1 class='hero-animation'>Sentiment Analysis</h1>")

    st.info("Please click the button twice if it is't working.")

    st.header(st.session_state.current_post["title"])
    st.write(st.session_state.current_post["text"])

    st.write(f"Reddit Post URL: {st.session_state.current_post['url']}")
    
    st.divider()
    comment = st.text_input(label="Put your comment here:")
    
    col1, col2 = st.columns([1, 12])
    
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
                        f'<div style="position: absolute; right: 50%; width: {abs(score) * 50}%; height: 100%; background-color: #db4444; border-radius: 10px 0 0 10px;"></div>' 
                        if score < 0 else 
                        f'<div style="position: absolute; left: 50%; width: {score * 50}%; height: 100%; background-color: #38ab38; border-radius: 0 10px 10px 0;"></div>'
                        if score > 0 else 
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
        st.rerun()

    # --- Download Section ---
    st.divider()
    st.subheader("Download Reddit Data")

    # Button to trigger the data fetch
    if st.button("Prepare Reddit Data (CSV)"):
        try:
            with st.spinner("Fetching Reddit data..."):
                download_response = requests.get(f"{BASE_URL}/download-reddit-data")
                if download_response.status_code == 200:
                    content_disposition = download_response.headers.get('content-disposition')
                    filename = f"aggregated_reddit_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
                    if content_disposition:
                        parts = content_disposition.split('filename=')
                        if len(parts) > 1:
                            filename = parts[1].strip('"')
                    
                    st.session_state.reddit_download_content = download_response.content
                    st.session_state.reddit_download_filename = filename
                    st.success("Aggregated Reddit data is ready for download below.")
                else:
                    st.session_state.reddit_download_content = None
                    st.session_state.reddit_download_filename = None
                    st.error(f"Error fetching data for download: {download_response.status_code} - {download_response.text}")
        except Exception as e:
            st.session_state.reddit_download_content = None
            st.session_state.reddit_download_filename = None
            st.error(f"Error during aggregated Reddit data download request: {str(e)}")

    # Conditionally display the download button if data is ready
    if st.session_state.reddit_download_content is not None:
        st.download_button(
            label="Click here to download Reddit Data CSV",
            data=st.session_state.reddit_download_content,
            file_name=st.session_state.reddit_download_filename,
            mime='text/csv',
            key='download-reddit-agg-final' 
        )
    # --- End Download Section ---

    # --- Add Matplotlib Sentiment Metrics Chart ---
    st.divider()
    st.subheader("Recent Sentiment Metrics") 
    
    # Fetch data for the chart
    with st.spinner("Loading aggregated Reddit data for chart..."):
        agg_reddit_df_chart = get_aggregated_reddit_data()

    if agg_reddit_df_chart is not None and not agg_reddit_df_chart.empty:
        try:
            required_cols = ['Date', 'percentage_positive', 'average_upvote_ratio']
            if not all(col in agg_reddit_df_chart.columns for col in required_cols):
                st.warning("Aggregated Reddit data is missing required columns for the chart.")
            else:
                agg_reddit_df_chart['Date'] = pd.to_datetime(agg_reddit_df_chart['Date']).dt.date # Ensure only date part is used for uniqueness check
                agg_reddit_df_chart = agg_reddit_df_chart.sort_values('Date')

                # --- Add check for number of unique dates ---
                unique_dates = agg_reddit_df_chart['Date'].nunique()
                if unique_dates < 3: # Example threshold, adjust as needed
                    st.warning(f"Warning: The chart data only includes {unique_dates} unique date(s). This might be due to limited data availability from the source.")
                # --- End check ---

                # --- Debug: Show the DataFrame ---
                st.caption("Data being plotted:")
                st.dataframe(agg_reddit_df_chart)
                # --- End Debug ---

                # Explicitly clear any previous plot on the figure
                plt.clf() 
                fig_sentiment, ax3 = plt.subplots(figsize=(15, 4)) 
                
                ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax3.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10)) 
                
                plt.xticks(rotation=45, ha='right')
                ax3.set_xlabel('Date')

                # Plotting percentage positive
                ax3.plot(agg_reddit_df_chart['Date'], agg_reddit_df_chart['percentage_positive'], 'g-o', label='% Positive') # Added marker 'o'
                ax3.set_ylabel('Percentage Positive', color='g')
                ax3.tick_params(axis='y', labelcolor='g')
                
                # Plotting average upvote ratio on twin axis
                ax3_twin = ax3.twinx()
                ax3_twin.plot(agg_reddit_df_chart['Date'], agg_reddit_df_chart['average_upvote_ratio'], 'b-^', label='Avg Upvote Ratio') # Added marker '^'
                ax3_twin.set_ylabel('Average Upvote Ratio', color='b')
                ax3_twin.tick_params(axis='y', labelcolor='b')

                # Updated Title
                ax3.set_title('Sentiment Metrics for Last Up To 20 Available Days') 
                
                # Combine legends
                lines3, labels3 = ax3.get_legend_handles_labels()
                lines3_twin, labels3_twin = ax3_twin.get_legend_handles_labels()
                ax3.legend(lines3 + lines3_twin, labels3 + labels3_twin, loc='upper left')

                ax3.grid(True, linestyle='--', alpha=0.6)
                plt.tight_layout()
                st.pyplot(fig_sentiment)
                # Updated Caption
                st.caption("This chart shows the aggregated % Positive Sentiment and Average Upvote Ratio for up to the 20 most recent dates with available Reddit posts.") 
        except Exception as e:
            st.error(f"Error generating Sentiment Metrics chart: {e}")
    else:
        # Updated Warning
        st.warning("Aggregated Reddit data not available for Sentiment Metrics chart.") 
    # --- End Matplotlib Chart ---

else:
    st.error("No Reddit posts with text content available.")
    if st.button("Reload posts"):
        st.session_state.reddit_data = get_reddit_data()
        st.session_state.seen_posts = set()
        st.session_state.pop("current_post", None)
        st.session_state.reddit_download_content = None
        st.session_state.reddit_download_filename = None
        st.rerun()
