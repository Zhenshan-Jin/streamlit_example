import time
import logging
from pydaisi import Daisi
import streamlit as st
import pandas as pd
import os

logging.getLogger().setLevel(logging.INFO)

st.text_input("search query", key="query")

# query = "apple"
# call google news to get data
gn_d = Daisi("GoogleNews JSON", base_url="https://dev3.daisi.io")
wc_d = Daisi("WordCloud JSON", base_url="https://dev3.daisi.io")
if st.session_state.query:
    x = gn_d.get_news(query=st.session_state.query, num=50)
    # x = gn_d.get_news(query=query)
    news = pd.DataFrame(x.get_result()["result"])

    # display a list of news 
    news_for_display = news[["title", "date", "link"]]
    st.write(f"Here is the search result for {st.session_state.query}")
    st.dataframe(news_for_display)

    # call word cloud to build the word cloud out of it 
    wc_texts = [{"id": i, "title": r['title']} for i, r in news.iterrows()]
    y = wc_d.generate_wordcloud(texts=wc_texts)
    wordcloud = y.get_result()
    st.image([wordcloud[1]["src"], wordcloud[2]["src"]]])