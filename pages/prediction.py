import pathlib
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)

BASE_URL = "http://127.0.0.1:6969"

st.html("<h1 class='hero-animation'>Bitcoin Dashboard</h1>")
st.html("Real-time Bitcoin price analysis and prediction")

col1, col2 = st.columns([2, 1])

def get_bitcoin_data():
    try:
        response = requests.get(f"{BASE_URL}/bitcoin")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            st.error(f"Error fetching Bitcoin data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

def get_prediction():
    try:
        response = requests.get(f"{BASE_URL}/result")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching prediction: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return None

dashboard_container = st.container()

if 'preprocess_data_content' not in st.session_state:
    st.session_state.preprocess_data_content = None
if 'preprocess_data_filename' not in st.session_state:
    st.session_state.preprocess_data_filename = None
if 'price_data_content' not in st.session_state:
    st.session_state.price_data_content = None
if 'price_data_filename' not in st.session_state:
    st.session_state.price_data_filename = None

with dashboard_container:
    with st.spinner("Loading Bitcoin data..."):
        bitcoin_df = get_bitcoin_data()
    
    with col1:
        st.subheader("Bitcoin Price (Last 30 Days)")
        
        if bitcoin_df is not None:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=bitcoin_df['date'],
                    y=bitcoin_df['price'],
                    mode='lines',
                    name='BTC Price',
                    line=dict(color='#F7931A', width=2)
                )
            )
            
            fig.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(211, 211, 211, 0.5)'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(211, 211, 211, 0.5)',
                    title="Price (USD)"
                ),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Daily Open vs Close Price")
            try:
                btc_daily_df = bitcoin_df.set_index('date')
                
                daily_agg = btc_daily_df['price'].resample('D').agg(['first', 'last'])
                daily_agg.rename(columns={'first': 'Open', 'last': 'Close'}, inplace=True)
                daily_agg.dropna(inplace=True)
                
                if not daily_agg.empty:
                    fig_mpl, ax = plt.subplots(figsize=(15, 4))
                    ax.plot(daily_agg.index, daily_agg['Open'], label='Open', marker='o', linestyle='-', markersize=4)
                    ax.plot(daily_agg.index, daily_agg['Close'], label='Close', marker='x', linestyle='--', markersize=4)
                    
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Price (USD)')
                    ax.set_title('Bitcoin Daily Open vs Close Price')
                    
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
                    plt.xticks(rotation=45, ha='right')
                    
                    ax.legend()
                    ax.grid(True, linestyle='--', alpha=0.6)
                    plt.tight_layout()
                    
                    st.pyplot(fig_mpl)
                else:
                    st.warning("Could not generate daily Open/Close data.")

            except Exception as e:
                st.error(f"Error generating Open/Close chart: {e}")

            if not bitcoin_df.empty:
                latest_price = bitcoin_df['price'].iloc[-1]
                first_price = bitcoin_df['price'].iloc[0]
                price_change = latest_price - first_price
                price_change_pct = (price_change / first_price) * 100
                
                st.metric(
                    label="Current Bitcoin Price", 
                    value=f"${latest_price:,.2f}", 
                    delta=f"{price_change_pct:.2f}% in 30 days"
                )
        else:
            st.error("Unable to load Bitcoin price data")
    
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.button("Refresh Data"):
        st.session_state.preprocess_data_content = None
        st.session_state.preprocess_data_filename = None
        st.session_state.price_data_content = None
        st.session_state.price_data_filename = None
        st.rerun()

    st.markdown("---") 
    st.subheader("Download Data")
    
    dl_col1, dl_col2 = st.columns(2)

    with dl_col1:
        if st.button("Prepare Preprocessed Sentiment Data (CSV)"):
            try:
                with st.spinner("Fetching preprocessed data..."):
                    download_response = requests.get(f"{BASE_URL}/download-preprocess-data")
                    if download_response.status_code == 200:
                        content_disposition = download_response.headers.get('content-disposition')
                        filename = f"preprocessed_bitcoin_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
                        if content_disposition:
                            parts = content_disposition.split('filename=')
                            if len(parts) > 1:
                                filename = parts[1].strip('"')
                        
                        st.session_state.preprocess_data_content = download_response.content
                        st.session_state.preprocess_data_filename = filename
                        st.success("Preprocessed data is ready for download below.")
                    else:
                        st.session_state.preprocess_data_content = None
                        st.session_state.preprocess_data_filename = None
                        st.error(f"Error fetching data for download: {download_response.status_code} - {download_response.text}")
            except Exception as e:
                st.session_state.preprocess_data_content = None
                st.session_state.preprocess_data_filename = None
                st.error(f"Error during preprocessed data download request: {str(e)}")

        if st.session_state.preprocess_data_content is not None:
            st.download_button(
                label="Click here to download Preprocessed Data CSV",
                data=st.session_state.preprocess_data_content,
                file_name=st.session_state.preprocess_data_filename,
                mime='text/csv',
                key='download-preprocess-final'
            )

    with dl_col2:
        if st.button("Prepare Bitcoin Price Data (CSV)"):
            if bitcoin_df is not None and not bitcoin_df.empty:
                try:
                    with st.spinner("Preparing price data..."):
                        csv_buffer = io.StringIO()
                        bitcoin_df.to_csv(csv_buffer, index=False, encoding='utf-8')
                        csv_data = csv_buffer.getvalue()
                        
                        filename = f"bitcoin_price_last_30_days_{datetime.now().strftime('%Y%m%d')}.csv"
                        
                        st.session_state.price_data_content = csv_data
                        st.session_state.price_data_filename = filename
                        st.success("Bitcoin price data is ready for download below.")
                except Exception as e:
                    st.session_state.price_data_content = None
                    st.session_state.price_data_filename = None
                    st.error(f"Error generating Bitcoin price CSV: {str(e)}")
            else:
                st.session_state.price_data_content = None
                st.session_state.price_data_filename = None
                st.warning("Bitcoin price data is not available to prepare.")

        if st.session_state.price_data_content is not None:
            st.download_button(
                label="Click here to download Bitcoin Price CSV",
                data=st.session_state.price_data_content,
                file_name=st.session_state.price_data_filename,
                mime='text/csv',
                key='download-price-final'
            )
    
    st.markdown("---") 

    with col2:
        st.subheader("Price Prediction")
        
        with st.spinner("Loading bitcoin price prediction..."):
            prediction = get_prediction()

        if prediction:
            direction = prediction.get('direction', 'unknown')
            confidence = prediction.get('confident', '0%')
            
            prediction_card = f"""
            <div class="hi-playwright" style="background-color: {'#38ab38' if direction == 'up' else '#db4444'}; padding: 20px; border-radius: 10px; text-align: center;">
                <h3>Prediction: {direction.upper()}</h3>
                <div style="font-size: 3.5rem; margin: 15px 0;">
                    {'📈' if direction == 'up' else '📉'}
                </div>
                <p style="font-size: 1.2rem;">Confidence: <strong>{confidence}%</strong></p>
            </div>
            """
            st.html(prediction_card)

            st.html("<h3>Market Statistics</h3>")
            
            if bitcoin_df is not None and not bitcoin_df.empty:
                max_price = bitcoin_df['price'].max()
                min_price = bitcoin_df['price'].min()
                avg_price = bitcoin_df['price'].mean()
                volatility = bitcoin_df['price'].std()
                
                col_stats1, col_stats2 = st.columns(2)
                
                with col_stats1:
                    st.metric("30D High", f"${max_price:,.2f}")
                    st.metric("30D Average", f"${avg_price:,.2f}")
                
                with col_stats2:
                    st.metric("30D Low", f"${min_price:,.2f}")
                    st.metric("Volatility", f"${volatility:,.2f}")
        else:
            st.error("Unable to load prediction data")

