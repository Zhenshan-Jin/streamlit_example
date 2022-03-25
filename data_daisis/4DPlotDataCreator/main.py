import pycountry_convert as pc
from functools import reduce
import pandas as pd

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

def create_data(x, y, z):
    x = x.rename(columns={"Value": "Value_x"})
    y = y.rename(columns={"Value": "Value_y"})
    z = z.rename(columns={"Value": "Value_z"})
    valid_codes = set(x["Code"]) & set(y["Code"]) & set(z["Code"])
    country_code_data = {c: alpha3_to_country_name_continent(c) for c in valid_codes}
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