import sqlalchemy as sa
import urllib
import pandas as pd
import requests

def LoadingLine(userId, token) :
    url = "https://api.line.me/v2/bot/chat/loading/start"
    userIdLine = userId
    tokenLineBot = token
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+tokenLineBot
    }
 
    data = {
        "chatId": userIdLine,
        "loadingSeconds": 10
    }
    
    response = requests.post(url, headers=headers, json=data)
    # print("Status Code", response.status_code)
    # print("JSON Response ", response.json())