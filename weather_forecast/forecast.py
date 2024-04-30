import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz


def get_weather_next_12_hours(location, current_time, token):
    future_time = current_time + timedelta(days=1)
    current_date = current_time.strftime('%Y-%m-%d')
    future_date = future_time.strftime('%Y-%m-%d')
    url = (f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{current_date}/'
           f'{future_date}')
    params = {
        'key': token,
        'unitGroup': "metric",
        'contentType': 'json',
        "include": "hours"
    }
    response = requests.get(url, params=params)
    response = response.json()
    weather_by_hour = []
    global_info = [response[info] for info in response if info != "days" and info != "queryCost"]
    for info in global_info:
        if info == "Kyiv":
            global_info[global_info.index(info)] = "Київ"
        elif info == "Суми, Україна":
            global_info[global_info.index(info)] = "Суми"
    if len(global_info) > 6:
        global_info = global_info[:6]
    column_city = ["city_" + str(info) for info in response if info != "days" and info != "queryCost" and info != "stations"]
    for day in response["days"]:
        template = [str(day[info]) for info in day if info != "hours"]
        columns_days = ["day_" + info for info in day if info != "hours"]
        for hour in day["hours"]:
            hour_info = [str(hour[info]) for info in hour]
            columns_hour = ["hour_" + str(info) for info in hour]
            full_info_hour = global_info + template + hour_info
            weather_by_hour.append(full_info_hour)
    rounded_time = current_time.replace(second=0, microsecond=0, minute=0) + timedelta(
        hours=round(current_time.minute / 60))
    formatted_time = rounded_time.strftime('%H:%M:%S')
    dt_object = datetime.strptime(formatted_time, '%H:%M:%S')
    dt_object += timedelta(hours=3)
    updated_time_string = dt_object.strftime('%H:%M:%S')
    weather_current_hour = next((item for item in weather_by_hour if item[42] == updated_time_string), None)
    index_current = weather_by_hour.index(weather_current_hour)
    forecast_next_12_hours = weather_by_hour[index_current+1:][:12]
    columns = column_city + columns_days + columns_hour
    forecast_next_12_hours.insert(0, columns)
    df = pd.DataFrame(forecast_next_12_hours[1:], columns=forecast_next_12_hours[0])
    return df


def forecast_all_regions(token, data_folder, current_time):
    regions = pd.read_csv(data_folder + '/regions.csv')
    pd_list = []
    for name in regions["center_city_ua"]:
        if name == "Київ":
            pd_list.append(get_weather_next_12_hours("Kyiv", current_time, token))
        elif name == "Суми":
            pd_list.append(get_weather_next_12_hours("Суми, Україна", current_time, token))
        else:
            pd_list.append(get_weather_next_12_hours(name, current_time, token))
    full_forecast = pd.concat(pd_list)
    full_forecast.to_csv(data_folder + "/forecast_next_12_hours_all_regions.csv", index=False)


if __name__ == "__main__":
    with open('token.json', 'r') as file:
        data = json.load(file)

    TOKEN = data.get('token', None)
    DATA_FOLDER = "data"
    utc_time = datetime.utcnow()
    #kyiv_timezone = pytz.timezone('Europe/Kiev')
    #current_time = datetime.now(kyiv_timezone)
    forecast_all_regions(TOKEN, DATA_FOLDER, utc_time)



