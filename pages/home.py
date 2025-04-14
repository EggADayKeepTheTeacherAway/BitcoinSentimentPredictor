import streamlit as st
import pathlib

# Load CSS
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
        <p>Get a prediction for future Bitcoin trends and today price.</p>
    </div>
    <div class="card">
        <h2>Sentiment Analysis</h2>
        <p>See that your comment positive or negative.</p>
    </div>
    <div class="card">
        <h2>API</h2>
        <p>See out API doccumentation here.</p>
    </div>
</div>
""")
