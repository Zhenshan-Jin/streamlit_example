import pandas as pd

DATA_NAME = "Life expectancy"

def query(): 
    data = pd.read_csv("life-expectancy.csv")
    data.rename(columns={"Life expectancy": "Value"}, inplace=True)
    data = data[["Year", "Code", "Value"]]
    return DATA_NAME, data