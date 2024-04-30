import os, sys
import json
import regex as re
import calendar
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import sklearn.preprocessing as preprocessing
from sklearn.preprocessing import StandardScaler


def get_for_predict():
    def to_vector_preprocessing(text, stop_words: list):
        if not stop_words:
            stop_words = stopwords.words("english")
        stemmer = PorterStemmer()
        text_array = word_tokenize(re.sub('[\W\s\d]', ' ', text.lower()))
        processed_text = ' '.join(
                [
                stemmer.stem(word) for word in text_array
                if (len(word) > 2) and (word not in stop_words)
                ])
        return processed_text

    def tfidf_vectorization(_corpus):
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(_corpus)
        sparse_matrix = pd.DataFrame(
            X.todense(),
            columns=vectorizer.get_feature_names_out())
        return sparse_matrix

    # prepare all data for predict
    PATH_TO_MODULES = 'files_for_prediction'
    DATA_FOLDER = "files_for_prediction/data"
    sys.path.append(PATH_TO_MODULES)

    # get features' data
    from get_info_from_api import get_all_regions_info_and_prepare
    get_all_regions_info_and_prepare(DATA_FOLDER).to_csv(DATA_FOLDER + "/features_for_prediction.csv")

    # features
    features = pd.read_csv(DATA_FOLDER + "/features_for_prediction.csv", index_col=0)

    # get ISW data for last day
    from isw_parse import parser, writer, clean_data
    DIR_ISW = DATA_FOLDER + "/isw_for_last_day.csv"
    date = datetime.now().date() - timedelta(days=1)
    start_date, end_date = date, date
    parsed = parser(start_date, end_date)
    writer(parsed, DIR_ISW)
    clean_data(DIR_ISW)

    from forecast import forecast_all_regions

    with open(PATH_TO_MODULES + '/token.json', 'r') as file:
        data = json.load(file)

    TOKEN = data.get('token', None)

    utc_time = datetime.utcnow()
    forecast_all_regions(TOKEN, DATA_FOLDER, utc_time)

    # import data
    isw_last_day = pd.read_csv(DATA_FOLDER + "/isw_for_last_day.csv")
    tg_12h = pd.read_csv(DATA_FOLDER + "/messages_today.csv")
    weather_data = pd.read_csv(DATA_FOLDER + "/forecast_next_12_hours_all_regions.csv")

    # stopwords
    langs = ['english', 'russian']
    stop_words = ['russian'] + list(map(lambda elem: elem.lower(), calendar.month_name))[1:]
    for lang in langs:
        stop_words += stopwords.words(lang)

    # processing isw for last day
    processed_isw = isw_last_day["main_text"].apply(
        lambda row: to_vector_preprocessing(row, stop_words)
    )
    isw_vectorized = tfidf_vectorization(processed_isw.tolist())

    # processing tg messages for last 12 hours
    processed_tg = tg_12h['message'].apply(
        lambda row: to_vector_preprocessing(row, stop_words)
    )
    tg_vectorized = tfidf_vectorization(processed_tg.tolist())

    # wrangle data inappropriates
    tg_vectorized[['date', 'time']] = tg_12h[['date', 'time']]
    isw_vectorized["date"] = pd.to_datetime(isw_last_day["date"], format='%d-%m-%Y')
    tg_vectorized["date"] = pd.to_datetime(tg_12h["date"], format='%Y-%m-%d')
    tg_vectorized["time"] = pd.to_datetime(tg_12h["time"], format='%H:%M:%S').dt.round('H')
    merged_sm = isw_vectorized.merge(tg_vectorized, how='outer', on="date")
    merged_sm = merged_sm.fillna(0)
    merged_sm.drop("time_y", axis=1, inplace=True)
    # print(merged_sm)
    # print(merged_sm["date"])
    merged_sm = merged_sm.groupby("date").sum()

    pca = PCA()
    new = pca.fit_transform(merged_sm)
    merged_sm_2 = pd.DataFrame(new)
    merged_sm_2['date'] = merged_sm.index
    merged_sm_2["date"] += timedelta(days=1)

    weather_cols = [
        'city_address', 'hour_datetimeEpoch', 'day_datetime', 'day_tempmax',
        'day_tempmin', 'day_temp', 'day_dew', 'day_humidity', 'day_precip', 'day_precipcover',
        'day_solarradiation', 'day_solarenergy', 'day_uvindex', 'day_moonphase',
        'hour_temp', 'hour_humidity', 'hour_precip', 'hour_precipprob',
        'hour_windgust', 'hour_windspeed', 'hour_winddir', 'hour_pressure',
        'hour_visibility', 'hour_cloudcover', 'hour_solarradiation',
        'hour_uvindex', 'hour_severerisk', 'hour_conditions'
    ]
    weather_final = weather_data[weather_cols]

    weather_final["day_datetime"] = pd.to_datetime(weather_final["day_datetime"], format='%Y-%m-%d')

    data_for_predict = weather_final.merge(merged_sm_2, left_on="day_datetime", right_on="date")
    data_for_predict["hour_datetime"] = pd.to_datetime(data_for_predict["hour_datetimeEpoch"], unit="s")

    # 336 is the number of columns after PCA for sparse matrix in final_data
    for i in range(2, 336):
        data_for_predict[i] = 0

    features["date"] = pd.to_datetime(features["date"])

    data = data_for_predict.merge(features, how="left", left_on=["hour_datetime", "city_address"], right_on=["date", "city"])

    cond_change = preprocessing.LabelEncoder()
    data["hour_conditions"] = cond_change.fit_transform(data["hour_conditions"])

    data.fillna(0, inplace=True)
    data = pd.get_dummies(data, columns=['city_address'], prefix="", prefix_sep="")
    data.drop(["city", "Сімферополь", "Луганськ", 'date_x', 'date_y',
               'hour_datetimeEpoch', "day_datetime"], axis=1, inplace=True)
    data.set_index("hour_datetime", inplace=True)
    data.columns = data.columns.astype(str)

    # save data
    # data.to_csv(DATA_FOLDER + "/final_data_for_predict.csv")

    import pickle
    with open(r"..\models\trained_models\1_logistic_reg_v2.pkl", 'rb') as m:
        log_reg = pickle.load(m)


    scaler=StandardScaler()
    scaled_data = scaler.fit_transform(data)
    test_data = pd.DataFrame(scaled_data, index=data.index, columns=data.columns)

    test = pd.DataFrame(test_data.iloc[:, 366:].idxmax(axis=1), columns=["city"])
    test["predict"] = log_reg.predict(test_data).tolist()

    test.to_csv("predict_data.csv")
    df = pd.read_csv('predict_data.csv')

    # Convert DataFrame to JSON
    json_data = {}
    json_data['last_model_train_time'] = "2024-04-09T16:15:31Z"
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    json_data['last_prediction_time'] = timestamp
    json_data['last_tg_update_time'] = "2024-04-21T18:03:13Z"

    for city, city_data in df.groupby('city'):
        city_dict = {}
        for date, alarm_info in zip(city_data['hour_datetime'], city_data['predict']):
            city_dict[date] = alarm_info
        json_data[city] = city_dict

    # Save JSON data to a file
    with open('predict.json', 'w', encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    get_for_predict()
