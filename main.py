import streamlit as st
import pandas as pd
import streamlit as st
from streamlit_navigation_bar import st_navbar

styles = {  
    "nav": {
        "height": "3.8rem"
    },

}

options = {
    "show_menu": True,
    "show_sidebar": False,
}

pages = [
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/prediction.py", title="Predict Result"),
    st.Page("pages/community.py", title="Data From The Community")
]

page = st_navbar(
    pages,
    styles=styles,
    options=options,

)

if page:
    page.run()