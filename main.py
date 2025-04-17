import streamlit as st
import pandas as pd
import pathlib
from streamlit_navigation_bar import st_navbar

# Get current project directory
project_dir = pathlib.Path.cwd()

# Create .streamlit directory if it doesn't exist
streamlit_dir = project_dir / ".streamlit"
streamlit_dir.mkdir(exist_ok=True)

# Create config.toml file with dark theme
config_path = streamlit_dir / "config.toml"
with open(config_path, "w") as f:
    f.write("[theme]\nbase = \"dark\"\n")


styles = {  
    "nav": {
        "height": "3.8rem",
        "background-color": "#1c1f20",
    },

}

options = {
    "show_menu": False,
    "show_sidebar": False,
}

st.set_page_config(layout="wide", page_title="Bitcoin Sentiment Predictor")

    
pages = [
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/prediction.py", title="Bitcoin"),
    st.Page("pages/community.py", title="Sentiment Analysis"),
    st.Page("pages/api.py", title="API"),
]

page = st_navbar(
    pages,
    styles=styles,
    options=options,

)

if page:
    page.run()

