import streamlit as st
import pandas as pd
from streamlit_navigation_bar import st_navbar

styles = {  
    "nav": {
        "height": "3.8rem",
        "background-color": "#1c1f20",
    },

}

options = {
    "show_menu": True,
    "show_sidebar": False,
}

st.set_page_config(layout="wide")
    
pages = [
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/prediction.py", title="Predict Result"),
    st.Page("pages/community.py", title="Data From The Community"),
    st.Page("pages/api.py", title="API"),
]

page = st_navbar(
    pages,
    styles=styles,
    options=options,

)

if page:
    page.run()