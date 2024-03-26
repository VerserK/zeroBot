from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,LocationSendMessage,URIAction
)

import sqlalchemy as sa
import urllib
import pandas as pd
import requests

BASE_URL = 'https://zerobotz.azurewebsites.net'

def ConnectDB(db):
    #configure sql server
    server = 'skcdwhprdmi.public.bf8966ba22c0.database.windows.net,3342'
    database =  db
    username = 'skcadminuser'
    password = 'DEE@skcdwhtocloud2022prd'
    driver = '{ODBC Driver 17 for SQL Server}'

    dsn = 'DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
    params = urllib.parse.quote_plus(dsn)
    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
    return engine

def getPos(sn):
    headers = {"Authorization": "Bearer e814eb26-c947-44f2-bd31-cc9aabfe841f"}
    urlID = f'https://wolf-prp-prod-head-api.propulsetelematics.com/wlf/api/users/me/search?search={sn}&start=0&limit=1'
    
    resID = requests.get(urlID, headers=headers)
    js = resID.json()
    
    if 'items' in js and js['items']:
        item = js['items'][0]
        last_position = item.get('lastPosition')
        if last_position is not None:
            coordinates = last_position.get('coordinates')
            Pos = [coordinates[1], coordinates[0]]
            return coordinates[1], coordinates[0] 
        else:
            return "Invalid serial number please try again !!"
    else:
        return "Invalid serial number please try again !!"
    
def getStatus(sn):
    headers = {"Authorization": "Bearer e814eb26-c947-44f2-bd31-cc9aabfe841f"}
    urlID = f'https://wolf-prp-prod-head-api.propulsetelematics.com/wlf/api/users/me/search?search={sn}&start=0&limit=1'
    
    resID = requests.get(urlID, headers=headers)
    js = resID.json()
    item = js['items'][0]
    status = statusKisTH(item.get('statusName'))
    return status

def statusKisTH(item):
    if item == 'ON':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'เปิด',picOn
    elif item == 'Long Idle':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'การทำงานเป็นเวลานาน,สตาร์ทไว้นาน แต่ยังไม่ขับ',picOn
    elif item == 'Key ON / Engine OFF':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'เปิดใช้งาน / ดับเครื่องยนต์',picOn
    elif item == 'Light Workload':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'งานไม่หนัก',picOn
    elif item == 'Idle':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'รอบเดินเบา',picOn
    elif item == 'Work':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'ทำงาน',picOn
    elif item == 'OFF':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power off_0.png'
        return 'ปิด',picOn
    elif item == 'ON / Idle':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power on_0.png'
        return 'เปิด/หยุดการทำงาน/พักการทำงาน',picOn
    elif item == '-none-':
        picOn = 'https://dwhwebstorage.blob.core.windows.net/pic/power off_0.png'
        return 'ไม่มี',picOn

def Allvalue(bubbleJS):
    flex_message = FlexSendMessage(
    alt_text='Flex Message',
    contents={
        "type": "carousel",
        "contents": bubbleJS
        }   
    )
    return flex_message

def bubble(url,ProductType,Model,VIN,UsageHour,SaleDate,SorgName,McName,ProfileId,urlMcName="https://liff.line.me/2000031997-L3QB36lz"):
# def bubble(url,ProductType,Model,VIN,SaleDate,SorgName,McName,ProfileId,urlMcName="https://liff.line.me/2000031997-L3QB36lz"):
    true = True
    bubbleJson =  {
        "type": "bubble",
        "hero": {
                "type": "image",
                "url": str(url),
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                "type": "uri",
                "uri": str(url)
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": str(ProductType),
                "weight": "bold",
                "size": "lg"
            },
            {
                "type": "separator",
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "ชื่อรถ :",
                        "color": "#818181",
                        "wrap": true
                    },
                    {
                        "type": "text",
                        "text": str(McName),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "lg"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "รุ่น :",
                        "color": "#818181",
                        "wrap": true
                    },
                    {
                        "type": "text",
                        "text": str(Model),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "หมายเลขรถ :",
                        "wrap": true,
                        "color": "#818181"
                    },
                    {
                        "type": "text",
                        "text": str(VIN),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "ชั่วโมงสะสม :",
                        "wrap": true,
                        "color": "#818181"
                    },
                    {
                        "type": "text",
                        "text": str(UsageHour),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "(รถติด KIS เท่านั้น)",
                        "wrap": true,
                        "color": "#818181",
                        "size": "xs"
                    }
                    ]
                }
                ],
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "วันที่ซื้อรถ :",
                        "wrap": true,
                        "color": "#818181"
                    },
                    {
                        "type": "text",
                        "text": str(SaleDate),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "sm"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": "ร้านที่ซื้อ :",
                        "wrap": true,
                        "color": "#818181"
                    },
                    {
                        "type": "text",
                        "text": str(SorgName),
                        "wrap": true
                    }
                    ]
                }
                ],
                "margin": "sm"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
            {
                "type": "button",
                "style": "primary",
                "height": "sm",
                "action": {
                "type": "uri",
                "label": "ตั้งชื่อรถของคุณที่นี่ !!",
                "uri": str(urlMcName+"?profileId="+ProfileId+"&vin="+VIN)
                },
                "color": "#F15922"
            }
            ],
            "flex": 0
        }
    }
    return bubbleJson

def callButtonBody(bodyVIN):
    flex_message = FlexSendMessage(
    alt_text='เลือกหมายเลขรถของคุณ',
    contents={
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
            "paddingAll": "20px",
            "backgroundColor": "#F25822",
            "spacing": "md",
            "height": "80px",
            "paddingTop": "22px",
            "background": {
                "type": "linearGradient",
                "angle": "12deg",
                "startColor": "#F25822",
                "endColor": "#FDB777",
                "centerColor": "#FD7F2C"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": bodyVIN
        }
        }
    )
    return flex_message

def CallButtonSelectByVIN(label, setDataName):
    CallButton = {
                "type": "button",
                "action": {
                "type": "message",
                "label": str(label),
                "text": str(setDataName)
                },
                "style": "secondary",
                "color": "#c0bfbf",
                "margin": "sm"
            }
    return CallButton

def CallButtonSelectByVINHistory(VIN, setDataName):
    CallButton = {
                "type": "button",
                "action": {
                "type": "uri",
                "label": str(setDataName),
                "uri": BASE_URL+"/history?VIN="+str(VIN)
                },
                "style": "secondary",
                "color": "#c0bfbf",
                "margin": "sm"
            }
    return CallButton

def CallLocVINText(ProductType,EquipmentName):
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
        }
        ]
    }
    }
    return Callloc

def locMap(EquipmentName,ProductType,latitude,longitude):
    loc = LocationSendMessage(
    title=str(EquipmentName),
    address=str(ProductType),
    latitude=str(latitude),
    longitude=str(longitude)
    )
    return loc

def statusOn(EquipmentName):
    callStatus = {
    "type": "bubble",
    "size": "mega",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "box",
            "layout": "baseline",
            "contents": [
            {
                "type": "text",
                "text": "สถานะรถของคุณ",
                "size": "xl",
                "weight": "bold",
                "color": "#ffffff",
                "margin": "sm",
                "align": "center",
                "gravity": "center",
                "wrap": True
            }
            ]
        }
        ],
        "paddingAll": "20px",
        "spacing": "md",
        "height": "96px",
        "paddingTop": "22px",
        "background": {
        "type": "linearGradient",
        "angle": "12deg",
        "startColor": "#F25822",
        "endColor": "#FDB777",
        "centerColor": "#FD7F2C"
        }
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
        {
            "type": "image",
            "url": str(getStatus(EquipmentName)[1]),
            "margin": "sm",
            "size": "md"
        },
        {
            "type": "text",
            "text": str(getStatus(EquipmentName)[0]),
            "weight": "bold",
            "align": "center",
            "wrap": True,
            "size": "lg",
            "margin": "lg"
        }
        ]
    }
    }

    return callStatus