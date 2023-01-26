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
            "size": "xs"
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
                "size": "xs",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(ProductType),
                "color": "#666666",
                "size": "xs",
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
                "size": "xs",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(EquipmentName),
                "size": "xs",
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
                "size": "xs",
                "color": "#aaaaaa"
            },
            {
                "type": "text",
                "text": str(Address),
                "color": "#666666",
                "size": "xs",
                "wrap": True
            }
            ]
        }
        ]
    }
    }
    return Callloc

# text = 'เลือกรหัส | KBCDZ552HL3F61515'
# cleantext = text.split("|")
# VINnumber = ''.join(cleantext[1])
# VINnumber = VINnumber.lstrip()
# con = ConnectDB('KIS Data')
# with con.begin() as conn:
#     qryVIN = sa.text(''' SELECT [Equipment_ID]
#             ,[Equipment_Name]
#             ,[Product]
#             ,[Subscription_End_Date]
#             ,[Subscription_Status]
#             ,[SKL]
#             ,[Subscription_Type]
#             ,[Subscription_Date]
#             ,[UpdateTime] FROM Engine_Detail WHERE [Equipment_Name] = (:VINnumber) ORDER BY [Equipment_Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY
#     ''')
#     vincheck =  con.execute(qryVIN, VINnumber=VINnumber)
#     vincheck_dict = vincheck.mappings().all()
#     if len(vincheck_dict) == 0:
#         print('ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS')
#     else:    
#         qry = sa.text(''' SELECT CRM.[Product Type] , KIS.[EquipmentName] , RAW.[latitude] , RAW.[longitude] , KIS.[SubDistrict] , KIS.[District] , KIS.[Province] , KIS.[Country] , KIS.[LastUpdate]
#             FROM [KIS Data].[dbo].[Engine_Location_Agg] KIS 
#             INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] CRM ON KIS.[EquipmentName] = CRM.[VIN] 
#             INNER JOIN [Raw Data].[dbo].[Engine_Location_Record] RAW ON KIS.[EquipmentName] = RAW.[equipmentName]
#             WHERE KIS.[EquipmentName] = (:VINnumber) AND KIS.[LastUpdate] = CAST( GETDATE() AS Date )
#             ORDER BY LastUpdate OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY ''')
#         resultset = conn.execute(qry, VINnumber=VINnumber)
#         results_as_dict = resultset.mappings().all()
#         print(results_as_dict)
#         if len(results_as_dict)==0:
#             print('รถของคุณไม่ถูกใช้งานในวันนี้ ทำให้ไม่สามารถระบุตำแหน่งปัจจุบันได้')
#         else:
#             queryEngineLocationAgg = []
#             for i in results_as_dict:
#                 ProductType = i['Product Type']
#                 EquipmentName = i['EquipmentName']
#                 latitude = i['latitude']
#                 longitude = i['longitude']
#                 SubDistrict = i['SubDistrict']
#                 District = i['District']
#                 Province = i['Province']
#                 Country = i['Country']
#                 Address = 'ต.'+ str(SubDistrict) + ' อ.' + str(District) + ' จ.' + str(Province) + ' ' + str(Country)
#                 queryEngineLocationAgg.append(CallLocVINText(ProductType,EquipmentName,Address))
#             flex_message = Allvalue(queryEngineLocationAgg)
#             print(flex_message)