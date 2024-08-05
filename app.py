from flask import Flask, request, abort, render_template, send_from_directory, flash, redirect, jsonify
from flask import url_for
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage,SourceUser,LocationSendMessage, RichMenu, RichMenuArea, RichMenuSize,
    RichMenuBounds, URIAction, MessageAction, FollowEvent, ImageSendMessage, VideoSendMessage, QuickReply, QuickReplyButton,ButtonsTemplate,PostbackAction,
    TemplateSendMessage, ImagemapSendMessage
)
from linebot.models.actions import RichMenuSwitchAction
from linebot.models.rich_menu import RichMenuAlias
from datetime import datetime, date, timedelta
from buttonLine import *
import sqlalchemy as sa
import urllib
import requests
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from pythainlp.util import thai_strftime
import logging
import json
from callApi import *

app = Flask(__name__)
app.secret_key = "flash message"

line_bot_api = LineBotApi('HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('43e76823a2c8d5a457d62a11a9c822cf')

BASE_URL = 'https://zerobotz.azurewebsites.net'
tokenLineBot = 'HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU='

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    url = 'https://webhook-lon.ants.co.th/LineWebhook/webhook/LRQI5wfE4'

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    #convert string to  object
    json_object = json.loads(body)
    # handle webhook body
    logging.info(json_object)
    try:
        handler.handle(body, signature)
        r = requests.post(url, json=json_object)
        logging.info(r)

    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text.find('ดูข้อมูลรถทั้งหมด') != -1:
        LoadingLine(event.source.user_id, tokenLineBot)
        profile = line_bot_api.get_profile(event.source.user_id)
        Userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("INSERT INTO [Line Data].[dbo].[log richmenu] "
                            "([UserId], [menu])"
                            "VALUES"
                            "('"+ Userid +"',N'ปุ่มข้อมูลรถทั้งหมด')")
            resultset = conn.execute(qry)

        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT PL.[Name],PL.[TaxId],PL.[ProfileId],IAC.[Firstname],IAC.[VIN],IAC.[Product Type],IAC.[Model],IAC.[Usage Hours],IAC.[Sale Date],IAC.[SOrg Name], MC.[Name] AS McName "
            "FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "LEFT JOIN [Line Data].[dbo].[MC Name] MC ON IAC.[VIN] = MC.[VIN]"
            "WHERE PL.[UserId] = '"+ Userid + "' AND IAC.[VIN] IS NOT NULL AND IAC.[Sale Date] IS NOT NULL"
            )
            resultset = conn.execute(qry)
            # results_as_dict = resultset.mappings().all()
            results_as_dict = pd.DataFrame(resultset.fetchall())
            results_as_dict = results_as_dict.drop_duplicates(subset=['VIN'], keep='last')
            results_as_dict = results_as_dict.to_dict('records')

            if len(results_as_dict)==0:
                Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            else:
                bubbleJsonZ = []
                if text == 'ดูข้อมูลรถทั้งหมด':
                    if len(results_as_dict) >= 5:
                        num = 5
                    else:
                        num = len(results_as_dict)
                else :
                    del results_as_dict[0:5]
                    num = len(results_as_dict)
                for i in range(num):
                    VINHours = results_as_dict[i]['VIN']
                    qryHour = sa.text("SELECT [Max_Hour] "
                    "FROM [App_View].[dbo].[KIS_Maxhour]"
                    "WHERE [Equipment_Name] = '" + VINHours + "'"
                    )
                    resultHours = conn.execute(qryHour)
                    resultHours_as_dict = resultHours.mappings().all()
                    ProductType = results_as_dict[i]['Product Type']
                    if ProductType == 'TRACTOR':
                        url = BASE_URL+'/image?name=tractopV2'
                    elif ProductType == 'MINI EXCAVATOR':
                        url = BASE_URL+'/image?name=miniV2'
                    elif ProductType == 'RICE TRANSPLANTER':
                        url = BASE_URL+'/image?name=riceV2'
                    elif ProductType == 'COMBINE HARVESTER':
                        url = BASE_URL+'/image?name=combineV2'
                    if ProductType == 'TRACTOR':
                        ProductType = 'รถแทรกเตอร์'
                    elif ProductType == 'MINI EXCAVATOR':
                        ProductType = 'รถขุด'
                    elif ProductType == 'RICE TRANSPLANTER':
                        ProductType = 'รถดำนา'
                    elif ProductType == 'COMBINE HARVESTER':
                        ProductType = 'รถเกี่ยวนวดข้าว'
                    Model = results_as_dict[i]['Model']
                    VIN = results_as_dict[i]['VIN']
                    if not resultHours_as_dict:
                        UsageHour = '-'
                    else:
                        for x in resultHours_as_dict:
                            UsageHour = x['Max_Hour']
                            UsageHour = ('{:,}'.format(UsageHour))
                            UsageHour = str(UsageHour).split('.')
                            UsageHour = UsageHour[0] + ' ชั่วโมง'
                    SaleDate = thai_strftime(results_as_dict[i]['Sale Date'], "%d %B %Y")
                    SorgName = results_as_dict[i]['SOrg Name']
                    if results_as_dict[i]['McName'] == None:
                        McName = '-'
                    else :
                        McName = results_as_dict[i]['McName']
                    ProfileId = results_as_dict[i]['ProfileId']
                    # SaleDate = i['Sale Date'].strftime("%d %B, %Y")
                    bubbleJsonZ.append(bubble(url,ProductType,Model,VIN,UsageHour,SaleDate,SorgName,McName,ProfileId))
                    # bubbleJsonZ.append(bubble(url,ProductType,Model,VIN,SaleDate,SorgName,McName,ProfileId))
                flex_message = Allvalue(bubbleJsonZ)
                if len(results_as_dict) > 5:
                    quickReply = TextSendMessage(text='คลิกเพื่อดูข้อมูลถัดไป', quick_reply=QuickReply(items=[QuickReplyButton(action=MessageAction(label="ดูข้อมูลถัดไป", text="ดูข้อมูลรถทั้งหมด_ถัดไป"))]))
                    line_bot_api.reply_message(event.reply_token,[flex_message, quickReply])
                else :
                    line_bot_api.reply_message(event.reply_token,flex_message)
    elif text == 'profile':
        LoadingLine(event.source.user_id, tokenLineBot)
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
    elif text == 'เช็กสถานะรถ':
        LoadingLine(event.source.user_id, tokenLineBot)
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("INSERT INTO [Line Data].[dbo].[log richmenu] "
                            "([UserId], [menu])"
                            "VALUES"
                            "('"+ userid +"',N'ปุ่มเช็กสถานะรถ')")
            resultset = conn.execute(qry)

        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT DISTINCT PL.[Name],PL.[TaxId],IAC.[Firstname],IAC.[VIN], MC.[Name] AS McName FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "LEFT JOIN [Line Data].[dbo].[MC Name] MC ON IAC.[VIN] = MC.[VIN]"
            "WHERE UserId = '"+ userid + "' AND IAC.[VIN] IS NOT NULL"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
            if len(results_as_dict)==0:
                Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            else:
                CallButtonJson = []
                for i in results_as_dict:
                    if i['McName'] != None:
                        label = i['McName']
                        setDataName = 'เลือกดูสถานะ | '+i['VIN']+' | '+i['McName']
                    else:
                        label = i['VIN']
                        setDataName = 'เลือกดูสถานะ | '+i['VIN']+' | (1)'
                    CallButtonJson.append(CallButtonSelectByVIN(label, setDataName))
                flex_message = callButtonBody(CallButtonJson)
                line_bot_api.reply_message(event.reply_token,flex_message)

    elif text == 'ค้นหารถ':
        LoadingLine(event.source.user_id, tokenLineBot)
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("INSERT INTO [Line Data].[dbo].[log richmenu] "
                            "([UserId], [menu])"
                            "VALUES"
                            "('"+ userid +"',N'ปุ่มดูตำแหน่งรถ')")
            resultset = conn.execute(qry)

        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT DISTINCT PL.[Name],PL.[TaxId],IAC.[Firstname],IAC.[VIN], MC.[Name] AS McName FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "LEFT JOIN [Line Data].[dbo].[MC Name] MC ON IAC.[VIN] = MC.[VIN]"
            "WHERE UserId = '"+ userid + "' AND IAC.[VIN] IS NOT NULL"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
            if len(results_as_dict)==0:
                Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            else:
                CallButtonJson = []
                for i in results_as_dict:
                    if i['McName'] != None:
                        label = i['McName']
                        setDataName = 'เลือกรหัส | '+i['VIN']+' | '+i['McName']
                    else:
                        label = i['VIN']
                        setDataName = 'เลือกรหัส | '+i['VIN']+' | (1)'
                    CallButtonJson.append(CallButtonSelectByVIN(label, setDataName))
                flex_message = callButtonBody(CallButtonJson)
                line_bot_api.reply_message(event.reply_token,flex_message)
    elif 'เลือกรหัส' in text:
        LoadingLine(event.source.user_id, tokenLineBot)
        cleantext = text.split("|")
        VINnumber = ''.join(cleantext[1])
        VINnumber = VINnumber.lstrip()

        McNameCheck = ''.join(cleantext[2])
        McNameCheck = McNameCheck.lstrip()

        if McNameCheck != '':
            con = ConnectDB('Line Data')
            with con.begin() as conn:
                qryCheckMcName = sa.text("SELECT [Name] "
                        "FROM [MC Name] WHERE [Name] = N'" + McNameCheck + "'"
                        "ORDER BY [Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
                )
                mcName =  conn.execute(qryCheckMcName)
                mcName_dict = mcName.mappings().all()
            if len(mcName_dict) != 0:
                McName = mcName_dict[0]['Name']
            else :
                McName = ''
        else :
            McName = ''

        con = ConnectDB('KIS Data')
        with con.begin() as conn:
            qryVIN = sa.text("SELECT [Equipment_ID],[Equipment_Name],[Product],[Subscription_End_Date],[Subscription_Status],[SKL]"
                    ",[Subscription_Type],[Subscription_Date],[UpdateTime] "
                    "FROM [KIS Data].[dbo].[Engine_Detail] WHERE [Equipment_Name] = '" + VINnumber + "'"
                    "ORDER BY [Equipment_Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
            )
            vincheck =  conn.execute(qryVIN)
            vincheck_dict = vincheck.mappings().all()
            if len(vincheck_dict) == 0:
                noneKIS = 'ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneKIS))
            else:
                qry = sa.text("SELECT DISTINCT CRM.[Product Type], CRM.[VIN] "
                    "FROM [CRM Data].[dbo].[ID_Address_Consent] CRM "
                    "WHERE CRM.[VIN] = '" + VINnumber + "' AND CRM.[VIN] IS NOT NULL"
                    )
                resultset = conn.execute(qry)
                results_as_dict = resultset.mappings().all()
                # if len(results_as_dict)==0:
                #     noneLocation = 'รถของคุณไม่ถูกใช้งานในวันนี้ ทำให้ไม่สามารถระบุตำแหน่งปัจจุบันได้'
                #     line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneLocation))
                # else:
                queryEngineLocationAgg = []
                for i in results_as_dict:
                    ProductType = i['Product Type']
                    if McName != '':
                        setDataName = McName
                    else :
                        setDataName = i['VIN']
                    latitude = getPos(i['VIN'])[0]
                    longitude = getPos(i['VIN'])[1]
                    queryEngineLocationAgg.append(CallLocVINText(ProductType,setDataName))
                flex_message = Allvalue(queryEngineLocationAgg)
                location_message = locMap(setDataName,ProductType,latitude,longitude)
                # line_bot_api.reply_message(event.reply_token,[flex_message,location_message])
                line_bot_api.reply_message(event.reply_token,location_message)
    elif 'เลือกดูสถานะ' in text:
        LoadingLine(event.source.user_id, tokenLineBot)
        cleantext = text.split("|")
        VINnumber = ''.join(cleantext[1])
        VINnumber = VINnumber.lstrip()

        McNameCheck = ''.join(cleantext[2])
        McNameCheck = McNameCheck.lstrip()

        if McNameCheck != '':
            con = ConnectDB('Line Data')
            with con.begin() as conn:
                qryCheckMcName = sa.text("SELECT [Name] "
                        "FROM [MC Name] WHERE [Name] = N'" + McNameCheck + "'"
                        "ORDER BY [Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
                )
                mcName =  conn.execute(qryCheckMcName)
                mcName_dict = mcName.mappings().all()
            if len(mcName_dict) != 0:
                McName = mcName_dict[0]['Name']
            else :
                McName = ''
        else :
            McName = ''

        con = ConnectDB('KIS Data')
        with con.begin() as conn:
            qryVIN = sa.text("SELECT [Equipment_ID],[Equipment_Name],[Product],[Subscription_End_Date],[Subscription_Status],[SKL]"
                    ",[Subscription_Type],[Subscription_Date],[UpdateTime] "
                    "FROM [KIS Data].[dbo].[Engine_Detail] WHERE [Equipment_Name] = '" + VINnumber + "'"
                    "ORDER BY [Equipment_Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
            )
            vincheck =  conn.execute(qryVIN)
            vincheck_dict = vincheck.mappings().all()
            if len(vincheck_dict) == 0:
                noneKIS = 'ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneKIS))
            else:
                qry = sa.text("SELECT DISTINCT CRM.[Product Type], CRM.[VIN] "
                    "FROM [CRM Data].[dbo].[ID_Address_Consent] CRM "
                    "WHERE CRM.[VIN] = '" + VINnumber + "'AND CRM.[VIN] IS NOT NULL"
                    )
                resultset = conn.execute(qry)
                results_as_dict = resultset.mappings().all()
                uuu = []
                for i in results_as_dict:
                    VIN_onoff = i['VIN']
                    uuu.append(statusOn(VIN_onoff))
                flex_message = Allvalue(uuu)
                line_bot_api.reply_message(event.reply_token,flex_message)
    # elif text == 'เข้าสู่ระบบ':
    #     profile = line_bot_api.get_profile(event.source.user_id)
    #     userid = profile.user_id
    #     con = ConnectDB('Line Data')
    #     with con.begin() as conn:
    #         qry = sa.text("SELECT Name,TaxId,UserId FROM [Line Data].[dbo].[Profile Line] PL "
    #         "WHERE UserId = '" + userid + "'"
    #         "ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
    #         )
    #         resultset = conn.execute(qry)
    #         results_as_dict = resultset.mappings().all()
    #     if len(results_as_dict)==0:
    #         buttons_template = ButtonsTemplate(
    #             title='My buttons sample', text='Hello, my buttons', actions=[
    #                 URIAction(label='Go to line.me', uri='https://zerobotz.azurewebsites.net/register'),
    #             ])
    #         template_message = TemplateSendMessage(
    #             alt_text='Buttons alt text', template=buttons_template)
    #         line_bot_api.reply_message(event.reply_token, template_message)
    #             # Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
    #         # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
    #         # url = 'https://api.line.me/v2/bot/user/'+userid+'/richmenu/richmenu-8a9237957ad0ee5157e72d6bd5dd13aa'
    #         # headers = {'content-type': 'application/json','Authorization':'Bearer HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU='}
    #         # r = requests.post(url, headers=headers)
    #     else:
    #         url = 'https://api.line.me/v2/bot/user/'+userid+'/richmenu/richmenu-3d294128c3e987c17d056902d251eab0'
    #         headers = {'content-type': 'application/json','Authorization':'Bearer HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU='}
    #         r = requests.post(url, headers=headers)
    elif text == 'ประวัติบริการ':
        LoadingLine(event.source.user_id, tokenLineBot)
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("INSERT INTO [Line Data].[dbo].[log richmenu] "
                            "([UserId], [menu])"
                            "VALUES"
                            "('"+ userid +"',N'ปุ่มประวัติบริการ')")
            resultset = conn.execute(qry)

        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT PL.[Name],PL.[TaxId],IAC.[Firstname],IAC.[VIN], MC.[Name] AS McName FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "LEFT JOIN [Line Data].[dbo].[MC Name] MC ON IAC.[VIN] = MC.[VIN]"
            "WHERE UserId = '"+ userid + "' AND IAC.[VIN] IS NOT NULL"
            )
            resultset = conn.execute(qry)
            # results_as_dict = resultset.mappings().all()
            results_as_dict = pd.DataFrame(resultset.fetchall())
            results_as_dict = results_as_dict.drop_duplicates(subset=['VIN'], keep='last')
            results_as_dict = results_as_dict.to_dict('records')
            if len(results_as_dict) == 0:
                noneKIS = 'ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneKIS))
            else:
                CallButtonJson = []
                for i in results_as_dict:
                    if i['McName'] != None:
                        setDataName = i['McName']
                    else:
                        setDataName = i['VIN']
                    CallButtonJson.append(CallButtonSelectByVINHistory(i['VIN'], setDataName))
                flex_message = callButtonBody(CallButtonJson)
                line_bot_api.reply_message(event.reply_token,flex_message)
    else:
        dataImageMap = imageMapForTextOther()
        line_bot_api.reply_message(event.reply_token,dataImageMap)
        pass
        # line_bot_api.reply_message(
        # event.reply_token,
        # TextSendMessage(text=event.message.text))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/image', methods=['GET'])
def openFolderImage():
    name = request.args.get('name')
    return send_from_directory(os.path.join(app.root_path, 'image'),name+'.png')

@app.route('/font', methods=['GET'])
def openFolderFont():
    name = request.args.get('name')
    return send_from_directory(os.path.join(app.root_path, 'font'),name+'.ttf')

@app.route('/image_insert', methods=['GET'])
def imageInsert():
    name = 'video_insert'
    return send_from_directory(os.path.join(app.root_path, 'image'),name+'.png')

@app.route('/media_insert', methods=['GET'])
def mediaInsert():
    name = 'วิดีโอแนะนำการใช้งาน'
    return send_from_directory(os.path.join(app.root_path, 'media'),name+'.mp4')

@app.route('/media_insert_preview', methods=['GET'])
def mediaInsertPreview():
    name = 'VDO ช่างจริงใจ'
    return send_from_directory(os.path.join(app.root_path, 'media'),name+'.png')

@app.route('/media_season', methods=['GET'])
def mediaSeason():
    name = 'ช่างจริงใจ'
    return send_from_directory(os.path.join(app.root_path, 'image'),name+'.jpg')

@app.route('/media_season_preview', methods=['GET'])
def mediaSeasonPreview():
    name = 'ช่างจริงใจPreview'
    return send_from_directory(os.path.join(app.root_path, 'image'),name+'.png')

@app.route('/register_mc_name', methods=['GET'])
def register_mc_name():
    return render_template('register_mc_name.html')

@app.route('/insert_mc_name', methods=['GET','POST'])
def insert_mc_name():
    message = {}
    VIN = request.args.get('vin')
    ProfileId = request.args.get('profileId')
    con = ConnectDB('CRM Data')
    with con.begin() as conn:
        qry = sa.text("SELECT [VIN],[Model],[Product Type] FROM [CRM Data].[dbo].[ID_Address_Consent] "
        "WHERE [VIN] = '"+ VIN + "'"
        "ORDER BY [VIN] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        )
        resultset = conn.execute(qry)
        results = resultset.mappings().all()

    if len(results) == 0:
        return "not data"

    if request.method == 'GET':
        if len(results) != 0:
            dataResponse = results[0]
            if dataResponse['Product Type'] == 'TRACTOR':
                ProductType = 'รถแทรกเตอร์'
            elif dataResponse['Product Type'] == 'MINI EXCAVATOR':
                ProductType = 'รถขุด'
            elif dataResponse['Product Type'] == 'RICE TRANSPLANTER':
                ProductType = 'รถดำนา'
            elif dataResponse['Product Type'] == 'COMBINE HARVESTER':
                ProductType = 'รถเกี่ยวนวดข้าว'
            
            sendResponse = {}
            sendResponse['vin'] = dataResponse['VIN']
            sendResponse['profileId'] = ProfileId
            sendResponse['model'] = dataResponse['Model']
            sendResponse['productType'] = ProductType
            return jsonify(sendResponse)
    if request.method == 'POST':
        if len(results) != 0:
            dataResponse = results[0]
            McName = request.form.get('McName')
            dateTime = datetime.today()
            dateTime = dateTime.strftime("%Y-%m-%d %H:%M:%S")
            if McName :
                con = ConnectDB('Line Data')
                with con.begin() as conn:
                    qry = sa.text("SELECT [ProfileId],[Name],[UserId] FROM [Line Data].[dbo].[Profile Line] "
                    "WHERE [ProfileId] = '"+ ProfileId + "'"
                    "ORDER BY [ProfileId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
                    )
                    profileLineset = conn.execute(qry)
                    resultProfileLine = profileLineset.mappings().all()
                
                if len(resultProfileLine) != 0:
                    con = ConnectDB('Line Data')
                    with con.begin() as conn:
                        qry = sa.text("SELECT [ProfileId],[VIN] FROM [Line Data].[dbo].[MC Name] "
                        "WHERE [VIN] = '"+ VIN + "'"
                        "ORDER BY [VIN] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
                        )
                        mcNameset = conn.execute(qry)
                        resultMcName = mcNameset.mappings().all()
                    if len(resultMcName) == 0:
                        con = ConnectDB('Line Data')
                        with con.begin() as conn:
                            insertData = sa.text("INSERT INTO [Line Data].[dbo].[Mc Name] "
                            "([ProductType], [Model], [VIN], [ProfileId], [Name], [CreateTime])"
                            "VALUES"
                            "('"+ dataResponse['Product Type'] +"','"+ dataResponse['Model'] +"','"+ VIN +"','"+ ProfileId +"',N'"+ McName +"','"+ dateTime +"')"
                            )
                            logging.info(insertData)
                            resultsetInsertData = conn.execute(insertData)
                        return "success"
                    else :
                        con = ConnectDB('Line Data')
                        with con.begin() as conn:
                            updateData = sa.text("UPDATE [Line Data].[dbo].[Mc Name] "
                            "SET [Name]=N'"+McName+"', [UpdateTime]='"+dateTime+"'"
                            "WHERE [VIN] = '"+ VIN + "'"
                            )
                            logging.info(updateData)
                            resultsetUpdateData = conn.execute(updateData)
                        return "success"
                else :
                    return "not user line"
            else :
                return "not mcName"

@app.route('/redirect_newkorp', methods=['GET','POST'])
def redirect_newkorp():
    return render_template('redirect_newkorp.html')

@app.route('/redirect_tokorp', methods=['GET','POST'])
def redirect_tokorp():
    userId = request.form.get('userId')
    kid = request.args.get('kid')
    
    # Establish database connection
    con = ConnectDB('Line Data')
    
    # Using parameterized query to prevent SQL injection
    qryLine = sa.text("SELECT [TaxId] FROM [Line Data].[dbo].[Profile Line] WHERE [Kubota ID] = :kid ORDER BY [Kubota ID] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY")
    
    with con.begin() as conn:
        resultChecUserId = conn.execute(qryLine, {"kid": kid})
        # Fetching all results as dictionary
        results_as_dict = resultChecUserId.fetchall()
    print(results_as_dict)
    # Checking if any result is returned
    if results_as_dict:
        # Convert results to DataFrame
        df = pd.DataFrame.from_records(results_as_dict)
        # Accessing the TaxId from DataFrame
        taxid = df.iloc[0][0]
        print(taxid)

        print(f"Redirecting with kid={kid}")
        return redirect(f"https://korp.siamkubota.co.th/Customer/callback_lon.php?kid={kid}")
    else:
        # Handle case where no result is found
        return redirect(f"https://liff.line.me/2000031997-mGrDYE4v")
    
@app.route('/redirects', methods=['GET','POST'])
def redirects():
    userId = request.form.get('userId')
    logging.info(userId)
    # userId = request.args.get('userId')
    # kid = request.args.get('kid')
    
    # Establish database connection
    con = ConnectDB('Line Data')
    
    # Using parameterized query to prevent SQL injection
    qryLine = sa.text("SELECT [Kubota ID] FROM [Line Data].[dbo].[Profile Line] WHERE [UserId] = :userId ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY")
    
    with con.begin() as conn:
        resultChecUserId = conn.execute(qryLine, {"userId": userId})
        # Fetching all results as dictionary
        results_as_dict = resultChecUserId.fetchall()
    print(results_as_dict)
    # Checking if any result is returned
    if results_as_dict:
        # Convert results to DataFrame
        df = pd.DataFrame.from_records(results_as_dict)
        # Accessing the TaxId from DataFrame
        kid = df.iloc[0][0]
        logging.info(kid)
        return kid
    else:
        logging.info('No user found with the given userId')
        return jsonify({"error": "No user found"}), 404

    #     print(f"Redirecting with kid={kid}")
    #     return redirect(f"https://korp.shinee.com/Customer/callback_lon.php?kid={kid}")
    # else:
    #     logging.info('Cant open')
    #     return "Cannot open", 400  # Returning a 400 Bad Request response with a message

@app.route('/register', methods=['GET','POST'])
def register():
    print('Request for index page received')
    return render_template('register.html')

@app.route('/insert_register', methods=['GET','POST'])
def insert_register():
    message = {}
    taxId = request.form.get('taxId')
    userId = request.form.get('userId')
    displayName = request.form.get('displayName')
    pictureUrl = request.form.get('pictureUrl')
    createTime = datetime.today() + timedelta(hours=7)
    createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
    status = '200'
    id = os.urandom(16).hex()

    con = ConnectDB('Line Data')
    with con.begin() as conn:
        qryLine = sa.text("SELECT [UserId] FROM [Line Data].[dbo].[Profile Line] "
        "WHERE [TaxId] = '"+ taxId +"' AND [TaxId] <> '3801100285099'"
        "ORDER BY [TaxId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        )
        resultCheckTaxId = conn.execute(qryLine)
        resultCheckTaxId_as_dict = resultCheckTaxId.mappings().all()
        dfCheckTaxId = pd.DataFrame.from_dict(resultCheckTaxId_as_dict)
    
    if len(dfCheckTaxId) != 0 :
        return "duplicate taxId"

    
    #check taxid
    con = ConnectDB('CRM Data')
    with con.begin() as conn:
        qry = sa.text("SELECT [KUBOTA ID],[Tax ID] FROM [CRM Data].[dbo].[ID_Address_Consent] "
        "WHERE [Tax ID] = '"+ taxId +"'"
        "ORDER BY [Tax ID] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        )
        resultset = conn.execute(qry)
        results_as_dict = resultset.mappings().all()
    df = pd.DataFrame.from_dict(results_as_dict)        
    kubotaid = df['KUBOTA ID'][0]
    #check userid
    with con.begin() as conn:
        qryLine = sa.text("SELECT [UserId] FROM [Line Data].[dbo].[Profile Line] "
        "WHERE [UserId] = '"+ userId +"'"
        "ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        )
        resultsetLine = conn.execute(qryLine)
        results_as_dict_line = resultsetLine.mappings().all()
        dfLine = pd.DataFrame.from_dict(results_as_dict_line)

    if request.method == 'POST':
        if taxId == '0123456789012':
            taxId = '3801100285099'
            kubotaid = '9000425492'

            con = ConnectDB('Line Data')
            with con.begin() as conn:
                insertData = sa.text("INSERT INTO [Line Data].[dbo].[Profile Line] "
                "([ProfileId], [Status], [Name], [Image], [UserId], [TaxId], [CreateTime],[Kubota ID])"
                "VALUES"
                "('"+ id +"','"+ status +"',N'"+ displayName +"','"+ pictureUrl +"','"+ userId +"','"+ taxId +"','"+ createTime +"','" + kubotaid + "')"
                )
                resultsetInsertData = conn.execute(insertData)
            url = 'https://api.line.me/v2/bot/user/'+userId+'/richmenu/richmenu-d0f8bcbf5f7c7ac33702f8cf83f4a48d'
            headers = {'content-type': 'application/json','Authorization':'Bearer HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU='}
            r = requests.post(url, headers=headers)

            messagePush = "คุณ "+displayName+" ได้ลงทะเบียนเรียบร้อยแล้ว สามารถศึกษาวิธีการใช้งานได้ที่วิดีโอด้านล่างครับ"
            # messagePush = 'ยินดีต้อนรับสู่ 🙏 ช่างจริงใจสยามคูโบต้า \n\n 👨🏻‍💼 ผู้ช่วยส่วนตัวของลูกค้าในการจัดการรถคูโบต้า \n\n 👇 กดที่ลิงก์ด้านล่าง เพื่อรับสิทธิ์ลุ้นรับนาฬิกาข้อมืออัจฉริยะ มูลค่า 1,290 บาท ฟรี!!! จำกัด 1 ท่าน/เรือน \n\n ⌚ https://forms.gle/7DtRjgwdcciB7EFRA'
            urlVideo = BASE_URL+'/media_insert'
            urlPreview = BASE_URL+'/media_insert_preview'
            videoMessage = VideoSendMessage(
                original_content_url=urlVideo,
                preview_image_url=urlPreview
            )
            line_bot_api.push_message(userId, [TextSendMessage(text=messagePush), videoMessage])
            return "success"
        elif len(df)==0:
            return "not taxId"
        elif len(dfLine)!=0:
            return "duplicate user"
        else:
            if results_as_dict[0]['KUBOTA ID'] == None or results_as_dict[0]['KUBOTA ID'] == '':
                return "not id ER"
            if results_as_dict[0]['Tax ID'] == None or results_as_dict[0]['Tax ID'] == '':
                return "not id ER"

            con = ConnectDB('Line Data')
            with con.begin() as conn:
                insertData = sa.text("INSERT INTO [Line Data].[dbo].[Profile Line] "
                "([ProfileId], [Status], [Name], [Image], [UserId], [TaxId], [CreateTime],[Kubota ID])"
                "VALUES"
                "('"+ id +"','"+ status +"',N'"+ displayName +"','"+ pictureUrl +"','"+ userId +"','"+ taxId +"','"+ createTime +"','" + kubotaid + "')"
                )
                resultsetInsertData = conn.execute(insertData)
            url = 'https://api.line.me/v2/bot/user/'+userId+'/richmenu/richmenu-d0f8bcbf5f7c7ac33702f8cf83f4a48d'
            headers = {'content-type': 'application/json','Authorization':'Bearer HvSWl3gV8+hLK5/2xb8Fejzg5QxJRdvtZiHf5irm0RiMpD6h1Owlj15XpwdHX6bVbXtfktmgXCEc0WmYzk/i8lKxNNCRnmo78QPupI9CVqvUTPaPtrbETMzLZcE+AKiEBK4CP7BzcE9Y2jy1YEDjRwdB04t89/1O/w1cDnyilFU='}
            r = requests.post(url, headers=headers)

            messagePush = "คุณ "+displayName+" ได้ลงทะเบียนเรียบร้อยแล้ว สามารถศึกษาวิธีการใช้งานได้ที่วิดีโอด้านล่างครับ"
            # messagePush = 'ยินดีต้อนรับสู่ 🙏 ช่างจริงใจสยามคูโบต้า \n\n 👨🏻‍💼 ผู้ช่วยส่วนตัวของลูกค้าในการจัดการรถคูโบต้า \n\n 👇 กดที่ลิงก์ด้านล่าง เพื่อรับสิทธิ์ลุ้นรับนาฬิกาข้อมืออัจฉริยะ มูลค่า 1,290 บาท ฟรี!!! จำกัด 1 ท่าน/เรือน \n\n ⌚ https://forms.gle/7DtRjgwdcciB7EFRA'
            urlVideo = BASE_URL+'/media_insert'
            urlPreview = BASE_URL+'/media_insert_preview'
            videoMessage = VideoSendMessage(
                original_content_url=urlVideo,
                preview_image_url=urlPreview
            )
            # urlPic = BASE_URL+'/media_season'
            # urlPicPreview = BASE_URL+'/media_season_preview'
            # picMessage = ImageSendMessage(
            #     original_content_url=urlPic,
            #     preview_image_url=urlPicPreview
            # )
            line_bot_api.push_message(userId, [TextSendMessage(text=messagePush), videoMessage])
            # line_bot_api.push_message(userId, [TextSendMessage(text=messagePush), picMessage])
            return "success"

@app.route('/history', methods=['GET','POST'])
def history():
    VIN = request.args.get('VIN')
    if request.args.get('num') == None:
        Limit = '10'
    else :
        Limit = request.args.get('num')
    con = ConnectDB('Service Data')
    if Limit == 'all':
        with con.begin() as conn:
            qry = sa.text("SELECT [VIN],[Vehicle Type Text],[LV Main Type],[Usage Hours],[Billing Date],[Billing Created On],[Symptom],[Net Value]"
            "FROM [Service Data].[dbo].[Service_Header]"
            "WHERE [VIN] = '"+ VIN +"'"
            "ORDER BY [Billing Date] Desc"
            )
            resultset = conn.execute(qry)
            data = resultset.mappings().all()
    else :
        with con.begin() as conn:
            qry = sa.text("SELECT [VIN],[Vehicle Type Text],[LV Main Type],[Usage Hours],[Billing Date],[Billing Created On],[Symptom],[Net Value]"
            "FROM [Service Data].[dbo].[Service_Header]"
            "WHERE [VIN] = '"+ VIN +"'"
            "ORDER BY [Billing Date] Desc OFFSET 0 ROWS FETCH NEXT "+Limit+" ROWS ONLY"
            )
            resultset = conn.execute(qry)
            data = resultset.mappings().all()
    
    lst = []
    for i in data:
        item = {}
        item['vin'] = i['VIN']
        item['vehicleType'] = i['Vehicle Type Text']
        item['lvMainType'] = i['LV Main Type']
        item['usageHours'] = i['Usage Hours']

        if i['Billing Date'] != None:
            Billing_Date = i['Billing Date']
            BDStr = datetime.strptime(str(Billing_Date),'%Y-%m-%d').date()
            listBillingDate = thai_strftime(BDStr, "%d %B %Y")
            # listBillingDate = str(i['Billing Date']).split('-')
            # item['billingDate'] = listBillingDate[2]+'-'+listBillingDate[1]+'-'+listBillingDate[0]
            item['billingDate'] = listBillingDate
        else :
            item['billingDate'] = ''
        
        if i['Billing Created On'] != None:
            Billing_Created_On = i['Billing Created On']
            BCOStr = datetime.strptime(str(Billing_Created_On),'%Y-%m-%d').date()
            listBillingCreatedOn = thai_strftime(BCOStr, "%d %B %Y")
            # listBillingCreatedOn = str(i['Billing Created On']).split('-')
            # item['billingCreatedOn'] = listBillingCreatedOn[2]+'-'+listBillingCreatedOn[1]+'-'+listBillingCreatedOn[0]
            item['billingCreatedOn'] = listBillingCreatedOn
        else :
            item['billingCreatedOn'] = ''

        item['symptom'] = i['Symptom']
        item['netValue'] = ('{:,}'.format(i['Net Value']))
        if i['Vehicle Type Text'] == 'รถแทรกเตอร์':
            image = 'tractop_history'
        elif i['Vehicle Type Text'] == 'รถแทรกเตอร์พร้อมอุปกรณ์ต่อพ่วง':
            image = 'tractop_history'
        elif i['Vehicle Type Text'] == 'รถขุด':
            image = 'mini_history'
        elif i['Vehicle Type Text'] == 'รถดำนา':
            image = 'rice_history'
        elif i['Vehicle Type Text'] == 'รถเกี่ยวนวดข้าว':
            image = 'combine_history'
        else:
            image = ''
        item['image'] = BASE_URL+'/image?name='+image
        lst.append(item)

    lstOption = ['10', '25', '50', '100', 'all']
    return render_template('historyV2.html', data=lst, options=lstOption, limit=Limit)

if __name__ == "__main__":
    app.run()