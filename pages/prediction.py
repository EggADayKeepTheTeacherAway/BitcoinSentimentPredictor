import pathlib
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)

# API Base URL
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

with dashboard_container:
    with st.spinner("Loading Bitcoin data..."):
        bitcoin_df = get_bitcoin_data()
    
    with st.spinner("Loading prediction..."):
        prediction = get_prediction()
    
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
    

    with col2:
        st.subheader("Price Prediction")
        
        if prediction:
            direction = prediction.get('direction', 'unknown')
            confidence = prediction.get('confident', '0%')
            
            prediction_card = f"""
            <div style="background-color: {'#38ab38' if direction == 'up' else '#db4444'}; padding: 20px; border-radius: 10px; text-align: center;">
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
    
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.button("Refresh Data"):
        pass