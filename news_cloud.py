from pydaisi import Daisi
import streamlit as st
import logging
import pandas as pd

logging.getLogger().setLevel(logging.INFO)

# Load Daisies 
googlenews_d = Daisi("GoogleNews JSON", base_url="https://dev3.daisi.io")
wordcloud_d = Daisi("WordCloud JSON", base_url="https://dev3.daisi.io")
location_d = Daisi("LocationExtraction", base_url="https://dev3.daisi.io")

# Create input widgets
st.text_input("search query", key="query")
limit = st.slider('Locations from top k news', min_value=10, max_value=50)  # 👈 this is a widget

if st.session_state.query:
    # Query News
    resp1 = googlenews_d.get_news(query=st.session_state.query, num=50)
    news = pd.DataFrame(resp1.get_result()["result"])[["title", "date", "link"]]
    texts = [r['title'] for i, r in news.iterrows()]
    st.dataframe(news)

    # Compute Wordcloud
    resp2 = wordcloud_d.generate_wordcloud(texts=texts)
    st.image(resp2.get_result()[1]["src"])
    
    # Extract Locations
    resp3 = location_d.get_locations(texts=texts[:limit])
    st.map(pd.DataFrame(resp3.get_result()["result"]))