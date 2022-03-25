import pandas as pd

DATA_NAME = "GDP per capita"
data = pd.read_csv("gdp-per-capita-worldbank.csv")
data.rename(columns={"GDP per capita, PPP (constant 2017 international $)": "Value"}, inplace=True)
data = data[["Year", "Code", "Value"]]

def query(): 
    return DATA_NAME, data