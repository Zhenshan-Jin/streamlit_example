import pandas as pd

DATA_NAME = "Milk - Excluding Butter - Food supply quantity (kg/capita/yr)"

def query(): 
    data = pd.read_csv("per-capita-milk-consumption.csv")
    data.rename(columns={"Milk - Excluding Butter - Food supply quantity (kg/capita/yr) (FAO, 2020)": "Value"}, inplace=True)
    data = data[["Year", "Code", "Value"]]
    return DATA_NAME, data