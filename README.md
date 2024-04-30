# Alarm Predictor

## Main goal
Our goal was to create a service that would be able to predict air alarms in the regions of Ukraine based on the weather on a given day and the previous day's report from the International Institute of War along with previous day's message from tg channel @war_monitor.
## Description of project
Based on the data that was provided by our Lecturer: air alarms history and weather history for all Ukrainian regions along with ISW reports and telegram messages that were scraped by our team we treained model and deployed it to AWS server.

## How to use our service
You need to send request to our server's endpoints (we reccomend using postman for this)
- In order to get recent alarm predict for all regions:
  http://13.53.113.166:8000/get_alarm with body
  {
    "location": "all"
}
- In order to get recent alarm predict for specific region:
  http://13.53.113.166:8000/get_alarm with body
  {
    "location": "Київ"

}
- In order to update prediction:
  http://13.53.113.166:8000/update_prediction
 If prediction was updated you will get following message : ""Prediction was successfully made!"" as answer to your request.

## Explaining project files 
1. isw_data.py - code for scaping and preprocessing data from isw reports
2. vectorized_isw.py - code for vectorizing isw data
3. gpaphs.py - code for visualisation of weather reports and analyzing other reports
4. final_pred.py - code to create dataset which is used to train model
5. raw-data - all data files which is used for predict in .csv format
6. server - folder which contains all files for server working

6.1. server/alarm_predicting.py - script to predict the alarm situation on the following 12 hours and writes the prediction to the file server/data/last_pred.json

6.2. server/get_alarm.py - server script that manages all requests made to the server, i.e. returns prediction for the specified location, if location is not specified, then prediction for all regions is retruned

7. models - folder which contains all models that our team have created during the course

7.1 models/model_training.ipynb - code that was used to train models.

7.2 models/model_stat.ipynb - notebook that can be used to look at the scores of the models during the training
