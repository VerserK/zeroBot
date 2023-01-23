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
    # connection = engine.connect()
    # metadata = sa.MetaData()
    # tablename = sa.Table(table, metadata, autoload=True, autoload_with=engine)
    # query = sa.select([tablename])
    # ResultProxy = connection.execute(query)
    # ResultSet = ResultProxy.fetchall()
    # df = pd.DataFrame(ResultSet)
    return engine

def Allvalue(TaxID,VIN):
    TaxID = TaxID
    VIN = VIN
    flex_message = FlexSendMessage(
    alt_text='hello',
    contents={
        "type": "carousel",
        "contents": [
            {
            "type": "bubble",
            "hero": {
                "type": "image",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_5_carousel.png"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "text",
                    "text": TaxID,
                    "wrap": True,
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                    {
                        "type": "text",
                        "text": VIN,
                        "wrap": True,
                        "weight": "bold",
                        "size": "xl",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": ".99",
                        "wrap": True,
                        "weight": "bold",
                        "size": "sm",
                        "flex": 0
                    }
                    ]
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
                    "action": {
                    "type": "uri",
                    "label": "Add to Cart",
                    "uri": "https://linecorp.com"
                    }
                },
                {
                    "type": "button",
                    "action": {
                    "type": "uri",
                    "label": "Add to wishlist",
                    "uri": "https://linecorp.com"
                    }
                }
                ]
            }
            },
            {
            "type": "bubble",
            "hero": {
                "type": "image",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_6_carousel.png"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "text",
                    "text": "Metal Desk Lamp",
                    "wrap": True,
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "flex": 1,
                    "contents": [
                    {
                        "type": "text",
                        "text": "$11",
                        "wrap": True,
                        "weight": "bold",
                        "size": "xl",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": ".99",
                        "wrap": True,
                        "weight": "bold",
                        "size": "sm",
                        "flex": 0
                    }
                    ]
                },
                {
                    "type": "text",
                    "text": "Temporarily out of stock",
                    "wrap": True,
                    "size": "xxs",
                    "margin": "md",
                    "color": "#ff5551",
                    "flex": 0
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
                    "flex": 2,
                    "style": "primary",
                    "color": "#aaaaaa",
                    "action": {
                    "type": "uri",
                    "label": "Add to Cart",
                    "uri": "https://linecorp.com"
                    }
                },
                {
                    "type": "button",
                    "action": {
                    "type": "uri",
                    "label": "Add to wish list",
                    "uri": "https://linecorp.com"
                    }
                }
                ]
            }
            },
            {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "flex": 1,
                    "gravity": "center",
                    "action": {
                    "type": "uri",
                    "label": "See more",
                    "uri": "https://linecorp.com"
                    }
                }
                ]
            }
            }
        ]
        }
    )
    return flex_message