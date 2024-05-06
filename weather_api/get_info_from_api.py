from datetime import datetime, timedelta
import pytz
import requests
import json
import pandas as pd
import time
import random
import urllib.request
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# with open('token.json', 'r') as file:
#     data = json.load(file)
#
# TOKEN = data.get('token', None)

# def get_number_neighbour_alarms():
#     url = f'https://api.ukrainealarm.com/api/v3/alerts'
#     headers = {
#         'accept': 'application/json',
#         'Authorization': TOKEN
#     }
#     response = requests.get(url, headers=headers)
#     data = response.json()
#     df = pd.DataFrame(data)
#     df = df[~df["regionId"].isin(["9999", "16"])]
#     regions = pd.read_csv('merged_ids.csv')
#     regions_list = [str(elem) for elem in list(regions['region_id_api'])]
#     df = df[df["regionId"].isin(regions_list)]
#     df.to_csv("alarms_current.csv", index=False)
#     return df.shape[0]


# def get_regions():
#     url = 'https://api.ukrainealarm.com/api/v3/regions'
#     headers = {
#         'accept': 'application/json',
#         'Authorization': TOKEN
#     }
#
#     response = requests.get(url, headers=headers)
#     data = response.json()
#     regions_name = []
#     regions_id = []
#     for info in data["states"]:
#         regions_name.append(info["regionName"].split()[0])
#         regions_id.append(info["regionId"])
#     del regions_name[18]
#     del regions_id[18]
#     regions_name[0] = "Київська"
#     regions_name[3] = "АР Крим"
#     regions_name = regions_name[:-1]
#     regions_id = regions_id[:-1]
#     alarms_api_ids = pd.DataFrame({'region_id_api': regions_id, 'region': regions_name})
#     alarms_api_ids.set_index('region', inplace=True)
#
#     alarms_api_ids.to_csv('alarms_api_ids.csv')
#     regions = pd.read_csv('../historical_data/regions.csv')
#     merged_ids = alarms_api_ids.merge(regions, on='region')
#     merged_ids.set_index('region', inplace=True)
#     merged_ids.to_csv('merged_ids.csv')


def str_to_utc(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    utc_0 = pytz.timezone('Etc/UTC')
    current_time = datetime_obj.astimezone(utc_0)
    #kyiv_timezone = pytz.timezone('Europe/Kiev')
    #current_time = datetime.now(kyiv_timezone)
    formatted_datetime = current_time.strftime('%Y-%m-%dT%H:%M:%S')
    return formatted_datetime


def get_alarm_number_for_region_last_n_hours(region_id, data_folder):
    final_info = generate_hourly_timestamps()
    current_time = datetime.utcnow()

    merged_id = pd.read_csv(data_folder + '/merged_ids.csv')
    api_id = merged_id[merged_id["region_id"] == region_id]["region_id_api"].iloc[0]
    url = f'https://siren.pp.ua/api/v3/alerts/regionHistory?regionId={api_id}'
    response = requests.get(url)
    while response.status_code != 200:
        time.sleep(0.5)
        response = requests.get(url)
    data = response.json()
    for elem in final_info:
        elem.append(merged_id.loc[merged_id["region_id"] == region_id, "center_city_ua"].values.tolist()[0])
        current_time = datetime.strptime(elem[0], '%Y-%m-%dT%H:%M:%S')
        current_time_minus_1 = current_time + timedelta(hours=-1)
        current_time_minus_3 = current_time + timedelta(hours=-3)
        current_time_minus_6 = current_time + timedelta(hours=-6)
        current_time_minus_12 = current_time + timedelta(hours=-12)
        current_time_minus_24 = current_time + timedelta(hours=-24)
        formatted_time_last_day = current_time_minus_24.strftime('%Y-%m-%d')
        formatted_time_minus_1 = current_time_minus_1.strftime('%Y-%m-%dT%H:%M:%S')
        formatted_time_minus_3 = current_time_minus_3.strftime('%Y-%m-%dT%H:%M:%S')
        formatted_time_minus_6 = current_time_minus_6.strftime('%Y-%m-%dT%H:%M:%S')
        formatted_time_minus_12 = current_time_minus_12.strftime('%Y-%m-%dT%H:%M:%S')

        count_minus_1 = 0
        count_minus_3 = 0
        count_minus_6 = 0
        count_minus_12 = 0
        count_minus_24 = 0

        for info in data[0]["alarms"]:
            if info["startDate"].startswith(formatted_time_last_day):
                count_minus_24 += 1
            if str_to_utc(info["startDate"]) >= formatted_time_minus_1:
                count_minus_1 += 1
            if str_to_utc(info["startDate"]) >= formatted_time_minus_3:
                count_minus_3 += 1
            if str_to_utc(info["startDate"]) >= formatted_time_minus_6:
                count_minus_6 += 1
            if str_to_utc(info["startDate"]) >= formatted_time_minus_12:
                count_minus_12 += 1
        final_info[final_info.index(elem)].extend([count_minus_24, count_minus_12, count_minus_6, count_minus_3, count_minus_1])
    return final_info


def generate_hourly_timestamps(start_time=None, num_hours=12):
    if start_time is None:
        start_time = datetime.utcnow()
        #kyiv_timezone = pytz.timezone('Europe/Kiev')
        #current_time = datetime.now(kyiv_timezone)
        #start_time = current_time
    else:
        start_time = start_time.replace(minute=0, second=0, microsecond=0)

    timestamps = []
    for i in range(num_hours):
        timestamp = start_time - timedelta(hours=i)
        timestamp_str = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        timestamp_str = timestamp_str[:-5] + '00:00'
        timestamps.append([timestamp_str])
    return timestamps

def get_all_regions_info_and_prepare(data_folder):
    full_info = []
    merged_id = pd.read_csv(data_folder + "/merged_ids.csv")
    regions = merged_id["region_id"]
    for region in regions:
        full_info.extend(get_alarm_number_for_region_last_n_hours(region, data_folder))
        time.sleep(0.5)
    full_info.insert(0, ["date", "city", "last_day_alarms", "last_12_hours_alarms", "last_6_hours_alarms", "last_3_hours_alarms", "last_1_hours_alarms"])
    for elem in full_info[1:]:
        elem[0] = elem[0].replace("T", " ")
    df = pd.DataFrame(full_info[1:], columns=full_info[0])
    #df.to_csv('alarms_info.csv', index=False)
    return df

#get_all_regions_info_and_prepare()





