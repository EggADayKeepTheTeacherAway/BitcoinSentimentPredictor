import streamlit as st
import pathlib

# Load CSS
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")

css_path = pathlib.Path("public/styles.css")
load_css(css_path)


st.html("""
<div class="hero">
    <h1>Bitcoin Predictor</h1>
</div>
""")

st.html("""
<div class="page-grid">
    <div class="card">
        <h2>Predict Result</h2>
        <p>Get a prediction for future Bitcoin trends.</p>
    </div>
    <div class="card">
        <h2>Data From The Community</h2>
        <p>Help improve the model with your comments (idk I need to ask Apple WTF should I do in this page).</p>
    </div>
    <div class="card">
        <h2>API</h2>
        <p>Access our prediction engine programmatically via API.</p>
    </div>
</div>
""")
