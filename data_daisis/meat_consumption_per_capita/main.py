import pandas as pd

DATA_NAME = "Meat food supply quantity (kg/capita/yr)"

def query(): 
    data = pd.read_csv("meat-consumption-vs-gdp-per-capita.csv")
    data.rename(columns={"Meat food supply quantity (kg/capita/yr) (FAO, 2020)": "Value"}, inplace=True)
    data = data[["Year", "Code", "Value"]]
    return DATA_NAME, data