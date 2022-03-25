import pandas as pd

DATA_NAME = "Life expectancy"
data = pd.read_csv("life-expectancy.csv")
data.rename(columns={"Life expectancy": "Value"}, inplace=True)
data = data[["Year", "Code", "Value"]]

def query(): 

    return DATA_NAME, data