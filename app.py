from datetime import datetime
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
line_bot_api = LineBotApi('95d3f32f9dbfa3821fb7e98748b99f4f')
handler = WebhookHandler('JQT2Sfk7ZZzXB9zZjoFDaI4OwWfmy3b8gNDLPx7G2lnaAo/3GZCPxW84MEr0GnerPuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIT2JLQVnsPn6rtpGAXQjkDaNYX52iyxzvfJOu8PI6tFtwdB04t89/1O/w1cDnyilFU=')

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == '__main__':
   app.run()