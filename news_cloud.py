import time
import logging
from pydaisi import Daisi
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pydeck as pdk

logging.getLogger().setLevel(logging.INFO)

st.text_input("search query", key="query")
limit = st.slider('x', min_value=10, max_value=50)  # 👈 this is a widget
st.write(f"locations for top {limit}")

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
    z = le_d.get_locations(texts=location_texts[:limit])
    rows = [{"name": i["address"], "lat": i["latitude"], "lon": i["longitude"]} for i in z.get_result()["result"]]
    map_df = pd.DataFrame(rows)
    st.map(map_df)
    
    # # hexagon_data = []
    # # for i in z.get_result()["result"]:
    # #     data_ = [{"lat": i["latitude"], "lng": i["longitude"], "entries"} for _ in range(len(i["address"]))]
    # #     hexagon_data.extend(data_)
    # # print(hexagon_data)
    # hexagon_data = [{"entries": len(i["address"]), "lat": i["latitude"], "lon": i["longitude"]} for i in z.get_result()["result"]]
    # print("\n================================")
    # rows = [{"name": i["address"], "lat": i["latitude"], "lon": i["longitude"]} for i in z.get_result()["result"]]
    # print(rows)
    # ALL_LAYERS = {
    #     "mentions": pdk.Layer(
    #         "HexagonLayer",
    #         data=hexagon_data,
    #         get_position=["lng", "lat"],
    #         radius=200,
    #         elevation_scale=4,
    #         elevation_range=[0, 1000],
    #         extruded=True,
    #     ),
    #     # "location_name": pdk.Layer(
    #     #     "TextLayer",
    #     #     data=rows,
    #     #     get_position=["lon", "lat"],
    #     #     get_text="name",
    #     #     get_color=[0, 0, 0, 200],
    #     #     get_size=15,
    #     #     get_alignment_baseline="'bottom'",
    #     # )
    # }
    # st.pydeck_chart(pdk.Deck(
    #     map_style="mapbox://styles/mapbox/light-v9",
    #     # initial_view_state={"latitude": 37.76,
    #     #                     "longitude": -122.4, "zoom": 11, "pitch": 50},
    #     layers=list(ALL_LAYERS.values()),
    # ))