import pandas as pd

DATA_NAME = "Population"
data = pd.read_csv("population.csv")
data.rename(columns={"Population (historical estimates)": "Value"}, inplace=True)
data = data[["Year", "Code", "Value"]]

def query(): 

    return DATA_NAME, data