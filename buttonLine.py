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
# con = ConnectDB('Line Data')
# with con.begin() as conn:
#     qry = sa.text('''SELECT Name,TaxId,[Firstname],[VIN],[Product Type],[Model],[Usage Hours],[Sale Date] FROM [Line Data].[dbo].[Profile Line] PL 
#     INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]
#     WHERE UserId = 'U97caf21a53b92919005e158b429c8c2b'
#     ''')
#     resultset = conn.execute(qry)
#     results_as_dict = resultset.mappings().all()
#     bubbleJsonZ = []
#     for i in results_as_dict:
#         ProductType = i['Product Type']
#         if ProductType == 'TRACTOR':
#             url = 'https://sv1.img.in.th/eQ7GO.png'
#         elif ProductType == 'MINI EXCAVATOR':
#             url = 'https://sv1.img.in.th/eQhBY.png'
#         elif ProductType == 'RICE TRANSPLANTER':
#             url = 'https://sv1.img.in.th/eQrpf.png'
#         elif ProductType == 'COMBINE HARVESTER':
#             url = 'https://sv1.img.in.th/e0pbC.png'
#         Model = i['Model']
#         VIN = i['VIN']
#         UsageHour = i['Usage Hours']
#         SaleDate = i['Sale Date'].strftime("%d %B, %Y")
#         bubbleJsonZ.append(bubble(url,ProductType,Model,VIN,UsageHour,SaleDate))
# flex_message = Allvalue(bubbleJsonZ)
# print(flex_message)