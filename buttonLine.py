from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,LocationSendMessage
)

import sqlalchemy as sa
import urllib
import pandas as pd

def ConnectDB(db):
    #configure sql server
    server = 'skcdwhprdmi.siamkubota.co.th'
    database =  db
    username = 'skcadminuser'
    password = 'DEE@skcdwhtocloud2022prd'
    driver = '{ODBC Driver 17 for SQL Server}'
    dsn = 'DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
    params = urllib.parse.quote_plus(dsn)
    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
    return engine

def Allvalue(bubbleJS):
    flex_message = FlexSendMessage(
    alt_text='zerosearch',
    contents={
        "type": "carousel",
        "contents": bubbleJS
        }   
    )
    return flex_message

def bubble(url,ProductType,Model,VIN,UsageHour,SaleDate):
    bubbleJson =  {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": str(url),
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
                    "text": str(ProductType),
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
                    "text": str(Model),
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
                    "text": str(VIN),
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
                    "text": str(UsageHour),
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
                    "text": str(SaleDate),
                    "color": "#666666",
                    "size": "sm",
                    "wrap": True,
                    "flex": 1
                }
                ]
            }
            ]
        },
        "size": "kilo"
        }
    return bubbleJson

def callButtonBody(bodyVIN):
    flex_message = FlexSendMessage(
    alt_text='hello',
    contents={
        "type": "carousel",
        "contents": [
            {
        "type": "bubble",
        "size": "giga",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "เลือกรถของคุณ",
                "color": "#FFFFFF",
                "size": "xl",
                "align": "center"
            }
            ],
            "backgroundColor": "#00A8A9"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": bodyVIN
        }
        }
        ]
        }
    )
    return flex_message

def CallButtonSelectByVIN(VIN):
    CallButton = {
                "type": "button",
                "action": {
                "type": "message",
                "label": str(VIN),
                "text": "เลือกรหัส | "+str(VIN)
                },
                "style": "primary",
                "color": "#343A3A",
                "margin": "sm"
            }
    return CallButton

def CallButtonSelectByVINHistory(VIN):
    CallButton = {
                "type": "button",
                "action": {
                "type": "uri",
                "label": str(VIN),
                "uri": "https://zerobotz.azurewebsites.net/history?vin="+str(VIN)
                },
                "style": "primary",
                "color": "#343A3A",
                "margin": "sm"
            }
    return CallButton

def CallLocVINText(ProductType,EquipmentName,Address):
    Callloc = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "text",
            "text": "ตำแหน่งรถของคุณ",
            "size": "xl",
            "weight": "bold"
        },
        {
            "type": "text",
            "text": "เฉพาะรถที่ติด KIS เท่านั้น",
            "size": "xs",
            "align": "center"
        }
        ]
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "box",
            "layout": "baseline",
            "contents": [
            {
                "type": "text",
                "text": "ผลิตภัณฑ์",
                "size": "sm",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(ProductType),
                "color": "#666666",
                "size": "sm",
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
                "size": "sm",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(EquipmentName),
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
                "text": "ตำแหน่งรถปัจจุบัน",
                "size": "sm",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(Address),
                "color": "#666666",
                "size": "sm",
                "wrap": True
            }
            ]
        }
        ]
    }
    }
    return Callloc

def locMap(EquipmentName,latitude,longitude,Address):
    loc = LocationSendMessage(
    title=str(EquipmentName),
    address=str(Address),
    latitude=str(latitude),
    longitude=str(longitude)
    )
    return loc

# userid = 'U97caf21a53b92919005e158b429c8c2b'
# con = ConnectDB('Line Data')
# with con.begin() as conn:
#     qry = sa.text("SELECT Name,TaxId,UserId FROM [Line Data].[dbo].[Profile Line] PL "
#     "WHERE UserId = '" + userid + "'"
#     "ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
#     )
#     resultset = conn.execute(qry)
#     results_as_dict = resultset.mappings().all()
    # print(len(results_as_dict))