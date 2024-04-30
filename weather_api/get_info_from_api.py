from datetime import datetime, timedelta
import pytz
import requests
import json
import pandas as pd

with open('token.json', 'r') as file:
    data = json.load(file)

TOKEN = data.get('token', None)


def get_number_neighbour_alarms():
    url = f'https://api.ukrainealarm.com/api/v3/alerts'
    headers = {
        'accept': 'application/json',
        'Authorization': TOKEN
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.DataFrame(data)
    df = df[~df["regionId"].isin(["9999", "16"])]
    regions = pd.read_csv('merged_ids.csv')
    regions_list = [str(elem) for elem in list(regions['region_id_api'])]
    df = df[df["regionId"].isin(regions_list)]
    df.to_csv("alarms_current.csv", index=False)
    return df.shape[0]


def get_number_alarms_for_region_last_24_hours(region_id):
    merged_id = pd.read_csv('merged_ids.csv')
    api_id = merged_id[merged_id["region_id"] == region_id]["region_id_api"].iloc[0]
    url = f'https://api.ukrainealarm.com/api/v3/alerts/regionHistory?regionId={api_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': TOKEN
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    count = 0
    utc_now = datetime.utcnow()
    kyiv_tz = pytz.timezone('Europe/Kiev')
    current_time = utc_now.astimezone(kyiv_tz)
    current_time = current_time+timedelta(hours=-24)
    formatted_time = current_time.strftime('%Y-%m-%d')
    for info in data[0]["alarms"]:
        print(info)
        if info["startDate"].startswith(formatted_time):
            count += 1
    return count

def get_regions():
    url = 'https://api.ukrainealarm.com/api/v3/regions'
    headers = {
        'accept': 'application/json',
        'Authorization': TOKEN
    }

    response = requests.get(url, headers=headers)
    data = response.json()
    regions_name = []
    regions_id = []
    for info in data["states"]:
        regions_name.append(info["regionName"].split()[0])
        regions_id.append(info["regionId"])
    del regions_name[18]
    del regions_id[18]
    regions_name[0] = "Київська"
    regions_name[3] = "АР Крим"
    regions_name = regions_name[:-1]
    regions_id = regions_id[:-1]
    alarms_api_ids = pd.DataFrame({'region_id_api': regions_id, 'region': regions_name})
    alarms_api_ids.set_index('region', inplace=True)

    alarms_api_ids.to_csv('alarms_api_ids.csv')
    regions = pd.read_csv('../historical_data/regions.csv')
    merged_ids = alarms_api_ids.merge(regions, on='region')
    merged_ids.set_index('region', inplace=True)
    merged_ids.to_csv('merged_ids.csv')


def str_to_utc(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')
    utc_0 = pytz.timezone('Etc/UTC')
    current_time = datetime_obj.astimezone(utc_0)
    formatted_datetime = current_time.strftime('%Y-%m-%dT%H:%M:%S')
    return formatted_datetime


def get_alarm_number_for_region_last_n_hours(region_id):
    merged_id = pd.read_csv('merged_ids.csv')
    api_id = merged_id[merged_id["region_id"] == region_id]["region_id_api"].iloc[0]
    url = f'https://api.ukrainealarm.com/api/v3/alerts/regionHistory?regionId={api_id}'
    headers = {
        'accept': 'application/json',
        'Authorization': TOKEN
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    current_time = datetime.utcnow()

    current_time_minus_1 = current_time + timedelta(hours=-1)
    current_time_minus_3 = current_time + timedelta(hours=-3)
    current_time_minus_6 = current_time + timedelta(hours=-6)
    current_time_minus_12 = current_time + timedelta(hours=-12)
    formatted_time_minus_1 = current_time_minus_1.strftime('%Y-%m-%dT%H:%M:%S')
    formatted_time_minus_3 = current_time_minus_3.strftime('%Y-%m-%dT%H:%M:%S')
    formatted_time_minus_6 = current_time_minus_6.strftime('%Y-%m-%dT%H:%M:%S')
    formatted_time_minus_12 = current_time_minus_12.strftime('%Y-%m-%dT%H:%M:%S')
    count_minus_1 = 0
    count_minus_3 = 0
    count_minus_6 = 0
    count_minus_12 = 0

    for info in data[0]["alarms"]:
        if str_to_utc(info["startDate"]) >= formatted_time_minus_1:
            count_minus_1 += 1
        if str_to_utc(info["startDate"]) >= formatted_time_minus_3:
            count_minus_3 += 1
        if str_to_utc(info["startDate"]) >= formatted_time_minus_6:
            count_minus_6 += 1
        if str_to_utc(info["startDate"]) >= formatted_time_minus_12:
            count_minus_12 += 1
    return [count_minus_1, count_minus_3, count_minus_6, count_minus_12]

# example of usage
# region_id = 10 -> Kyiv (merged_id.csv last column)
# print(get_alarm_number_for_region_last_n_hours(10))
# print(get_number_alarms_for_region_last_24_hours(10))
# print(get_number_neighbour_alarms())
