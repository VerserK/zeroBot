from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,SourceUser
)
import datetime
from buttonLine import *

app = Flask(__name__)

line_bot_api = LineBotApi('J9o+1YH2mYc/4RiFFOjgXTYqCIxT//ctqWgLjB4kyYlw8qaieSnNl42uyn/TMfk7PuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIRkiDDAVQ0PKiz2wreUTFBG4Vpv+hDtLSk1QAnu2V2pOwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7f9e03908fca984853b2fc322c1775c6')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text == 'ดูข้อมูลรถทั้งหมด':
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text('''SELECT Name,TaxId,[Firstname],[VIN],[Product Type],[Model],[Usage Hours],[Sale Date] FROM [Line Data].[dbo].[Profile Line] PL 
            INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]
            WHERE UserId = (:userid)
            ''')
            resultset = conn.execute(qry, userid=userid)
            results_as_dict = resultset.mappings().all()
            bubbleJsonZ = []
            for i in results_as_dict:
                ProductType = i['Product Type']
                if ProductType == 'TRACTOR':
                    url = 'https://sv1.img.in.th/eQ7GO.png'
                elif ProductType == 'MINI EXCAVATOR':
                    url = 'https://sv1.img.in.th/eQhBY.png'
                elif ProductType == 'RICE TRANSPLANTER':
                    url = 'https://sv1.img.in.th/eQrpf.png'
                elif ProductType == 'COMBINE HARVESTER':
                    url = 'https://sv1.img.in.th/e0pbC.png'
                Model = i['Model']
                VIN = i['VIN']
                UsageHour = i['Usage Hours']
                SaleDate = i['Sale Date'].strftime("%d %B, %Y")
                bubbleJsonZ.append(bubble(url,ProductType,Model,VIN,UsageHour,SaleDate))
            flex_message = Allvalue(bubbleJsonZ)
            line_bot_api.reply_message(event.reply_token,flex_message)
        # line_bot_api.reply_message(event.reply_token,flex_message)
    elif text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='Display name: ' + profile.display_name
                    ),
                    TextSendMessage(
                        text='Status message: ' + profile.status_message
                    ),
                    TextSendMessage(
                        text='Status message: ' + profile.user_id
                    )
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Bot can't use profile API without user ID"))
    elif text == 'ค้นหารถ':
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text('''SELECT Name,TaxId,[Firstname],[VIN] FROM [Line Data].[dbo].[Profile Line] PL 
            INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]
            WHERE UserId = (:userid)
            ''')
            resultset = conn.execute(qry, userid=userid)
            results_as_dict = resultset.mappings().all()
            CallButtonJson = []
            for i in results_as_dict:
                VIN = i['VIN']
                CallButtonJson.append(CellButtonSelectByVIN(VIN))
            flex_message = Allvalue(CallButtonJson)
            line_bot_api.reply_message(event.reply_token,flex_message)
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()