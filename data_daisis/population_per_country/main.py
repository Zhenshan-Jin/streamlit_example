import panadas as pd

DATA_NAME = "Population"

def query(): 
    data = pd.read_csv("population.csv")
    data.rename(columns={"Population (historical estimates)": "Value"}, inplace=True)
    data = data[["Year", "Code", "Value"]]
    return DATA_NAME, data