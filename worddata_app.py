import plotly.express as px
import streamlit as st
from pydaisi import Daisi
import logging
logging.getLogger().setLevel(logging.INFO)

# Daisi: query data 
x_daisi = Daisi(st.sidebar.selectbox('x', ("DataAPI GDPPerCapita",)), base_url="https://dev3.daisi.io")
y_daisi = Daisi(st.sidebar.selectbox('y', ("DataAPI MeatConsumptionPerCapita", "DataAPI LifeExpectancyPerCountry")), base_url="https://dev3.daisi.io")
z_daisi = Daisi(st.sidebar.selectbox('z', ("DataAPI PopulationPerCountry", "DataAPI MilkPerCapita")), base_url="https://dev3.daisi.io")
data_formater_daisi = Daisi("4DPlotDataFormater", base_url="https://dev3.daisi.io")

x_title, x = x_daisi.query().fetch_result()
y_title, y = y_daisi.query().fetch_result()
z_title, z = z_daisi.query().fetch_result()
df = data_formater_daisi.run(x, y, z).fetch_result()

# Streamlit: display data
# Widget to select displayed country names
default_countries = ["China", "Japan", "United States", "France", "Canada", "Russian Federation", "United Kingdom", "India", "Switzerland", "United Arab Emirates"]
symbols = st.sidebar.multiselect("Choose countries to visualize", set(df["Country"].to_list()), default_countries)

# Create the bubble plot
fig = px.scatter(df, x="Value_x", y="Value_y", size="Value_z", 
                 text=[i if i in symbols else "" for i in df["Country"]], color='Continent',
                 animation_frame='Year', animation_group='Country', 
                 log_x=True, log_y=False, size_max=40, hover_name="Country",
                 custom_data=['Value_x', 'Value_y', 'Value_z']
                 )
fig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{text}</b>: <br>",
        f"{x_title}: %{{customdata[0]}}",
        f"{y_title}: %{{customdata[1]}}",
        f"{z_title}: %{{customdata[2]}}"
    ])
)
fig.update_layout(
    title=f'{y_title} v. {x_title}',
    xaxis=dict(
        title=x_title,
        gridcolor='white',
        type='log',
        gridwidth=2,
    ),
    yaxis=dict(
        title=y_title,
        gridcolor='white',
        gridwidth=2,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)'
)
st.plotly_chart(fig, use_container_width=True)

# Create choropleth
fig = px.choropleth(df, locations="Code",
                    color="Value_y",
                    hover_name="Country",
                    animation_frame="Year",
                    animation_group='Country',
                    title = y_title,                 
                    color_continuous_scale=px.colors.sequential.PuRd,
                    width=1700, height=900,
                    custom_data=['Value_x', 'Value_y', 'Value_z', 'Country']
                    ) 
fig.update_traces(
    hovertemplate="<br>".join([
        "<b>%{customdata[3]}</b>: <br>",
        f"{x_title}: %{{customdata[0]}}",
        f"{y_title}: %{{customdata[1]}}",
        f"{z_title}: %{{customdata[2]}}"
    ])
)
fig.update_coloraxes(colorbar_len=1)
st.plotly_chart(fig, use_container_width=True)

