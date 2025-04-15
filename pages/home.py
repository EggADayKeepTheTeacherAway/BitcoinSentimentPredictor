import requests
import streamlit as st
import pathlib


def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)


st.html("""
<div class="hero hero-animation">
    <h1>Bitcoin Predictor</h1>
</div>
""")

st.html("""
<div class="page-grid">
    <div class="card">
        <h2>Bitcoin</h2>
<p>Obtain detailed predictions for future trends in Bitcoin, along with the current price for today. Stay informed about market movements and insights to help you make informed investment decisions.</p>    </div>
    <div class="card">
        <h2>Sentiment Analysis</h2>
        <p>See the analysis result of the emotional tone of any text. Discover whether the content is positive, negative, or neutral with detailed scoring and visualization of sentiment metrics.</p>
    </div>
    <div class="card">
        <h2>API</h2>
        <p>Integrate our powerful tools directly into your applications with our comprehensive API.</p>
    </div>
</div>
""")
