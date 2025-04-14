import streamlit as st
import pandas as pd


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

st.button("Press me sensei", key="green")
st.header("Header with divider", divider="rainbow")