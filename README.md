# Alarm Predictor

## Main goal
Our goal was to create a service that would be able to predict air alarms in the regions of Ukraine based on the weather on a given day and the previous day's report from the International Institute of War along with previous day's message from tg channel @war_monitor.
## Description of project
Based on the data that was provided by our Lecturer: air alarms history and weather history for all Ukrainian regions along with ISW reports and telegram messages that were scraped by our team we treained model and deployed it to AWS server.
## How to use our service
You have two options to use our service:
1. Website
Address - http://13.53.113.166:8000/

 - In order to retrieve most recent alarms data press button Get Alarm.

![Imgur](https://imgur.com/eq6Mf6n.jpg)

 - In order to update prediction press the button Update Prediction.

![Imgur][Imgur](https://imgur.com/nI6hZnh.jpg)
   
   
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
