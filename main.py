import streamlit as st
import pandas as pd
import streamlit as st
from streamlit_navigation_bar import st_navbar

page = st_navbar(["Home", "Documentation", "Examples", "Community", "About"])
st.write(page)


st.title("Bitcoin Predictor")
st.header("HEY GUYY")
st.subheader("hey")

st.markdown("This is _Markdown_")
st.caption("small text")

st.write("UWOOOOO 😊")  

code_example = """
def greet(name):
    print('hello', name)

"""

st.code(code_example, language="python")

st.divider()

st.subheader("Dataframe is coming")
df = pd.DataFrame({
    "Name": ['Alice', 'Bob', 'Charlie', 'David'],
    "Age": [25, 32, 37, 45],
    "Occupation": ["Engineer", "Doctor", "Artist", "Cheif"]
})

st.dataframe(df)

pressed = st.button("Press me sensei")
print(pressed)