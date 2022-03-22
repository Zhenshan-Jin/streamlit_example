import time
import logging
from pydaisi import Daisi
import streamlit as st
import pandas as pd
import os
from datetime import datetime

logging.getLogger().setLevel(logging.INFO)

st.text_input("search query", key="query")

# query = "china"
# call google news to get data
gn_d = Daisi("GoogleNews JSON", base_url="https://dev3.daisi.io")
wc_d = Daisi("WordCloud JSON", base_url="https://dev3.daisi.io")
le_d = Daisi("LocationExtraction", base_url="https://dev3.daisi.io")
if st.session_state.query:
    x = gn_d.get_news(query=st.session_state.query, num=50)
    # x = gn_d.get_news(query=query, num=3)
    news = pd.DataFrame(x.get_result()["result"])

    # display a list of news 
    news_for_display = news[["title", "date", "link"]]
    st.write(f"Here is the search result for {st.session_state.query}")
    st.dataframe(news_for_display)

    # call word cloud to build the word cloud out of it 
    wc_texts = [{"id": i, "title": r['title']} for i, r in news.iterrows()]
    y = wc_d.generate_wordcloud(texts=wc_texts)
    wordcloud = y.get_result()
    dat = datetime.now().strftime('%m/%d/%Y')
    st.image(wordcloud[1]["src"], f"What is about {st.session_state.query} today ({dat})")
    
    location_texts = [r['title'] for i, r in news.iterrows()]
    # for i, row in news.iterrows():
    z = le_d.get_locations(texts=location_texts[:10])
    rows = [{"lat": i["latitude"], "lon": i["longitude"]} for i in z.get_result()["result"]]
    map_df = pd.DataFrame(rows)
    st.map(map_df)