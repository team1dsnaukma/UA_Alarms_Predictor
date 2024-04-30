import pandas as pd

regions = pd.read_csv('../historical_data/regions.csv')
full_data = pd.read_csv('../full_data.csv')


data_final = pd.merge(full_data, regions[["region_id", "center_city_ua"]], left_on='region_city_x', right_on='center_city_ua')
data_final.drop(["center_city_ua", "region_city_x", "Unnamed: 0"], axis=1, inplace=True)
data_final.to_csv('data_final.csv')