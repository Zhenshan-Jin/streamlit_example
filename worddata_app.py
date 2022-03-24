import pandas as pd
import plotly.graph_objects as go
import pycountry_convert as pc
from functools import reduce
import plotly.express as px
import streamlit as st


# ----------------------------------------------------------------
# Convert to actual daisi API
# ----------------------------------------------------------------
class PyDaisi():
    @classmethod
    def get_daisis(cls, key):
        dic = {
            "x": ["z_milk_data_daisi", 'x_gdp_data_daisi', 'y_cancer_data_daisi'],
            "y": ["x_gdp_data_daisi", 'z_milk_data_daisi', 'y_cancer_data_daisi'],
            "z": ['y_cancer_data_daisi', 'z_milk_data_daisi', 'x_gdp_data_daisi']
        }
        return dic[key]

# # milk data API
# def z_milk_data_daisi():
#     milk = pd.read_csv("/Users/zhenshanjin/Documents/Belmont/sandy/UtilityDaisies/WordData/share-of-population-with-cancer.csv")
#     milk.rename(columns={"Prevalence - Neoplasms - Sex: Both - Age: Age-standardized (Percent)": "Value"}, inplace=True)
#     milk = milk[["Year", "Code", "Value"]]
#     return milk

# milk data API
def z_milk_data_daisi():
    milk = pd.read_csv("/Users/zhenshanjin/Documents/Belmont/sandy/UtilityDaisies/WordData/population.csv")
    milk.rename(columns={"Population (historical estimates)": "Value"}, inplace=True)
    milk = milk[["Year", "Code", "Value"]]
    return milk

# gdp data API
def x_gdp_data_daisi():
    gdp = pd.read_csv("/Users/zhenshanjin/Documents/Belmont/sandy/UtilityDaisies/WordData/gdp-per-capita-worldbank.csv")
    gdp.rename(columns={"GDP per capita, PPP (constant 2017 international $)": "Value"}, inplace=True)
    gdp = gdp[["Year", "Code", "Value"]]
    return gdp

# # cancer data API
# def y_cancer_data_daisi():
#     cancer = pd.read_csv("/Users/zhenshanjin/Documents/Belmont/sandy/UtilityDaisies/WordData/life-expectancy.csv")
#     cancer.rename(columns={"Life expectancy": "Value"}, inplace=True)
#     cancer = cancer[["Year", "Code", "Value"]]
#     return cancer

# cancer data API
def y_cancer_data_daisi():
    cancer = pd.read_csv("/Users/zhenshanjin/Documents/Belmont/sandy/UtilityDaisies/WordData/meat-consumption-vs-gdp-per-capita.csv")
    cancer.rename(columns={"Meat food supply quantity (kg/capita/yr) (FAO, 2020)": "Value"}, inplace=True)
    cancer = cancer[["Year", "Code", "Value"]]
    return cancer

def create_bubble_plot_data(x, y, z):
    # group by country code
    def alpha3_to_country_name_continent(alpha3):
        try:
            alpha2 = pc.country_alpha3_to_country_alpha2(alpha3)
            country = pc.country_alpha2_to_country_name(alpha2)
            continent_code = pc.country_alpha2_to_continent_code(alpha2)
            continent = pc.convert_continent_code_to_continent_name(continent_code)
        except:
            return "Unknown", "Unknown"
        return country, continent
    x = x.rename(columns={"Value": "Value_x"})
    y = y.rename(columns={"Value": "Value_y"})
    z = z.rename(columns={"Value": "Value_z"})
    valid_codes = set(x["Code"]) & set(y["Code"]) & set(z["Code"])
    country_code_data = {c: alpha3_to_country_name_continent(c) for c in valid_codes}
    # by_codes = {c: [] for c in valid_codes}
    x = x[x["Code"].isin(valid_codes)]
    y = y[y["Code"].isin(valid_codes)]
    z = z[z["Code"].isin(valid_codes)]
    
    df_final = reduce(lambda left,right: pd.merge(left,right,on=['Code', 'Year']), [x, y, z])
    df_final["Country"], df_final["Continent"] = [country_code_data[i][0] for i in df_final["Code"]], [country_code_data[i][1] for i in df_final["Code"]]
    df_final = df_final.sort_values("Year").reset_index(drop=True)
    
    # clean data
    df_final = df_final[df_final.Country != "Unknown"]
    df_final = df_final[df_final["Value_x"] > 450]
    df_final.dropna(inplace=True)
    return df_final


# ----------------------------------------------------------------
# Query data with Daisi
# ----------------------------------------------------------------
x_data_api = st.sidebar.selectbox('x', PyDaisi.get_daisis("x"))
y_data_api = st.sidebar.selectbox('y', PyDaisi.get_daisis("y"))
z_data_api = st.sidebar.selectbox('z', PyDaisi.get_daisis("z"))

milk = eval(x_data_api)()
gdp = eval(y_data_api)()
cancer = eval(z_data_api)()
df = create_bubble_plot_data(*[gdp, cancer, milk])

# ----------------------------------------------------------------
# Streamlit starts here!
# ----------------------------------------------------------------
default_texts = ["China", "Japan", "United States", "France", "Canada", "Russian Federation", "United Kingdom", "India", "Switzerland", "United Arab Emirates"]

symbols = st.sidebar.multiselect("Choose countries to visualize", df["Country"].to_list(), default_texts)


# Create the bubble plot
x_title = 'GDP per Capita($)'
y_title = 'Meat Supply Per Person (kg)'
fig = px.scatter(df, x="Value_x", y="Value_y",
	             size="Value_z", text=[i if i in symbols else "" for i in df["Country"]],
                 animation_frame='Year', animation_group='Country',
                 color='Continent', hover_name="Country", log_x=True, log_y=False, size_max=60)
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

# Create the world heatmap
fig = px.choropleth(df, locations="Code",
                    color="Value_y",
                    hover_name="Country",
                    animation_frame="Year",
                    animation_group='Country',
                    title = "Meat supply per person (kg)",                 
                    color_continuous_scale=px.colors.sequential.PuRd,
                    width=1700, height=900
                    ) 
fig.update_coloraxes(colorbar_len=1)
st.plotly_chart(fig, use_container_width=True)

