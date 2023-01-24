from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage
)

import sqlalchemy as sa
import urllib
import pandas as pd
import datetime

def ConnectDB(db):
    #configure sql server
    server = 'skcdwhprdmi.public.bf8966ba22c0.database.windows.net,3342'
    database =  db
    username = 'skcadminuser'
    password = 'DEE@skcdwhtocloud2022prd'
    driver = '{ODBC Driver 17 for SQL Server}'
    dsn = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password
    params = urllib.parse.quote_plus(dsn)
    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
    # connection = engine.connect()
    # metadata = sa.MetaData()
    # tablename = sa.Table(table, metadata, autoload=True, autoload_with=engine)
    # query = sa.select([tablename])
    # ResultProxy = connection.execute(query)
    # ResultSet = ResultProxy.fetchall()
    # df = pd.DataFrame(ResultSet)
    return engine

def Allvalue(bubbleJS):
    flex_message = FlexSendMessage(
    alt_text='hello',
    contents={
        "type": "carousel",
        "contents": bubbleJS
        }   
    )
    return flex_message

def bubble(ProductType,Model,VIN,UsageHour,SaleDate):
    bubbleJson = [{
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://www.w3schools.com/howto/img_avatar.png",
            "size": "full",
            "aspectMode": "cover",
            "aspectRatio": "20:13"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "ข้อมูลรถของคุณ",
                "size": "xl",
                "weight": "bold"
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "text",
                    "text": "ผลิตภัณฑ์",
                    "size": "sm",
                    "flex": 1,
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": ProductType,
                    "size": "sm",
                    "flex": 1,
                    "wrap": True, 
                    "color": "#666666"
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "text",
                    "text": "รุ่น",
                    "flex": 1,
                    "size": "sm",
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": Model,
                    "flex": 1,
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "text",
                    "text": "หมายเลขรถ",
                    "flex": 1,
                    "size": "sm",
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": VIN,
                    "flex": 1,
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "text",
                    "text": "ชั่วโมงสะสม (เฉพาะรุ่น KIS)",
                    "flex": 1,
                    "wrap": True,
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": UsageHour,
                    "flex": 1,
                    "size": "sm",
                    "wrap": True,
                    "color": "#666666"
                }
                ]
            },
            {
                "type": "box",
                "layout": "baseline",
                "contents": [
                {
                    "type": "text",
                    "text": "วันที่ซื้อรถ",
                    "flex": 1,
                    "size": "sm",
                    "color": "#aaaaaa"
                },
                {
                    "type": "text",
                    "text": SaleDate,
                    "color": "#666666",
                    "size": "sm",
                    "wrap": True,
                    "flex": 1
                }
                ]
            }
            ]
        }
        },
    {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": []
      }
    }]
    return bubbleJson

ProductType = 'MINI EXCAVATOR'
Model = 'KX033-4 KIS'
VIN = 'KBCCZ494VM3F30232'
UsageHour = '919'
SaleDate = '2565-01-15'
bubbleJsonZ = bubble(ProductType,Model,VIN,UsageHour,SaleDate)
flex_message = Allvalue(bubbleJsonZ)
print(flex_message)