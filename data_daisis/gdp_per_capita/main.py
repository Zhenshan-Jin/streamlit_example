import panadas as pd

DATA_NAME = "GDP per capita"

def query(): 
    data = pd.read_csv("gdp-per-capita-worldbank.csv")
    data.rename(columns={"GDP per capita, PPP (constant 2017 international $)": "Value"}, inplace=True)
    data = data[["Year", "Code", "Value"]]
    return DATA_NAME, data