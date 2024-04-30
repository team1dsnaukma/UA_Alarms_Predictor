# Alarm Predictor

## Main goal
Our goal was to create a service that would be able to predict air raids in the regions of Ukraine based on the weather on a given day and the previous day's report from the International Institute of War.
## Description of project
Based on the data that was provided by our Lecturer: air alarms history and weather history for all Ukrainian regions and ISW reports that were scraped by our team we treained model and deployed it to AWS server.

**Server endpoint** - http://54.172.227.220:8000

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
