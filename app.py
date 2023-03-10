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
    RichMenuBounds, URIAction, MessageAction, FollowEvent
)
from linebot.models.actions import RichMenuSwitchAction
from linebot.models.rich_menu import RichMenuAlias
from datetime import datetime, date
from buttonLine import *
import sqlalchemy as sa
import urllib
import requests
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from pythainlp.util import thai_strftime

app = Flask(__name__)
app.secret_key = "flash message"

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
        Userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT Name,TaxId,[Firstname],[VIN],[Product Type],[Model],[Usage Hours],[Sale Date] FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "WHERE PL.[UserId] = '"+ Userid + "'"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
            if len(results_as_dict)==0:
                Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            else:
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
                    if ProductType == 'TRACTOR':
                        ProductType = 'รถแทรกเตอร์'
                    elif ProductType == 'MINI EXCAVATOR':
                        ProductType = 'รถขุด'
                    elif ProductType == 'RICE TRANSPLANTER':
                        ProductType = 'รถดำนา'
                    elif ProductType == 'COMBINE HARVESTER':
                        ProductType = 'รถเกี่ยวนวดข้าว'
                    Model = i['Model']
                    VIN = i['VIN']
                    UsageHour = i['Usage Hours']
                    SaleDate = thai_strftime(i['Sale Date'], "%d %B %Y")
                    # SaleDate = i['Sale Date'].strftime("%d %B, %Y")
                    bubbleJsonZ.append(bubble(url,ProductType,Model,VIN,UsageHour,SaleDate))
                flex_message = Allvalue(bubbleJsonZ)
                line_bot_api.reply_message(event.reply_token,flex_message)
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
            qry = sa.text("SELECT Name,TaxId,[Firstname],[VIN] FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "WHERE UserId = '"+ userid + "'"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
            if len(results_as_dict)==0:
                Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            else:
                CallButtonJson = []
                for i in results_as_dict:
                    VIN = i['VIN']
                    CallButtonJson.append(CallButtonSelectByVIN(VIN))
                flex_message = callButtonBody(CallButtonJson)
                line_bot_api.reply_message(event.reply_token,flex_message)
    elif 'เลือกรหัส' in text:
        cleantext = text.split("|")
        VINnumber = ''.join(cleantext[1])
        VINnumber = VINnumber.lstrip()
        con = ConnectDB('KIS Data')
        with con.begin() as conn:
            qryVIN = sa.text("SELECT [Equipment_ID],[Equipment_Name],[Product],[Subscription_End_Date],[Subscription_Status],[SKL]"
                    ",[Subscription_Type],[Subscription_Date],[UpdateTime] "
                    "FROM Engine_Detail WHERE [Equipment_Name] = '" + VINnumber + "'"
                    "ORDER BY [Equipment_Name] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
            )
            vincheck =  conn.execute(qryVIN)
            vincheck_dict = vincheck.mappings().all()
            if len(vincheck_dict) == 0:
                noneKIS = 'ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneKIS))
            else:    
                qry = sa.text("SELECT CRM.[Product Type] , KIS.[EquipmentName] , RAW.[latitude] , RAW.[longitude] , KIS.[SubDistrict] , KIS.[District] , KIS.[Province] , KIS.[Country] , KIS.[LastUpdate]"
                    "FROM [KIS Data].[dbo].[Engine_Location_Agg] KIS "
                    "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] CRM ON KIS.[EquipmentName] = CRM.[VIN] "
                    "INNER JOIN [Raw Data].[dbo].[Engine_Location_Record] RAW ON KIS.[EquipmentName] = RAW.[equipmentName]"
                    "WHERE KIS.[EquipmentName] = '" + VINnumber + "' AND KIS.[LastUpdate] = CAST( GETDATE() AS Date )"
                    "ORDER BY LastUpdate OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
                    )
                resultset = conn.execute(qry)
                results_as_dict = resultset.mappings().all()
                print(results_as_dict)
                if len(results_as_dict)==0:
                    noneLocation = 'รถของคุณไม่ถูกใช้งานในวันนี้ ทำให้ไม่สามารถระบุตำแหน่งปัจจุบันได้'
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneLocation))
                else:
                    queryEngineLocationAgg = []
                    for i in results_as_dict:
                        ProductType = i['Product Type']
                        EquipmentName = i['EquipmentName']
                        latitude = i['latitude']
                        longitude = i['longitude']
                        SubDistrict = i['SubDistrict']
                        District = i['District']
                        Province = i['Province']
                        Country = i['Country']
                        Address = 'ต.'+ str(SubDistrict) + ' อ.' + str(District) + ' จ.' + str(Province) + ' ' + str(Country)
                        queryEngineLocationAgg.append(CallLocVINText(ProductType,EquipmentName,Address))
                    flex_message = Allvalue(queryEngineLocationAgg)
                    location_message = locMap(EquipmentName,latitude,longitude,Address)
                    line_bot_api.reply_message(event.reply_token,[flex_message,location_message])
    elif text == 'เข้าสู่ระบบ':
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT Name,TaxId,UserId FROM [Line Data].[dbo].[Profile Line] PL "
            "WHERE UserId = '" + userid + "'"
            "ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
        if len(results_as_dict)==0:
            Unregis = 'ไม่สามารถใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            url = 'https://api.line.me/v2/bot/user/'+userid+'/richmenu/richmenu-e2c275c4796b9f510fc33c384ab39f28'
            headers = {'content-type': 'application/json','Authorization':'Bearer J9o+1YH2mYc/4RiFFOjgXTYqCIxT//ctqWgLjB4kyYlw8qaieSnNl42uyn/TMfk7PuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIRkiDDAVQ0PKiz2wreUTFBG4Vpv+hDtLSk1QAnu2V2pOwdB04t89/1O/w1cDnyilFU='}
            r = requests.post(url, headers=headers)
        else:
            url = 'https://api.line.me/v2/bot/user/'+userid+'/richmenu/richmenu-3b63586f09b1876987b88a21007dda55'
            headers = {'content-type': 'application/json','Authorization':'Bearer J9o+1YH2mYc/4RiFFOjgXTYqCIxT//ctqWgLjB4kyYlw8qaieSnNl42uyn/TMfk7PuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIRkiDDAVQ0PKiz2wreUTFBG4Vpv+hDtLSk1QAnu2V2pOwdB04t89/1O/w1cDnyilFU='}
            r = requests.post(url, headers=headers)
    elif text == 'ประวัติบริการ':
        profile = line_bot_api.get_profile(event.source.user_id)
        userid = profile.user_id
        con = ConnectDB('Line Data')
        with con.begin() as conn:
            qry = sa.text("SELECT PL.[Name],PL.[TaxId],IAC.[Firstname],IAC.[VIN] FROM [Line Data].[dbo].[Profile Line] PL "
            "INNER JOIN [CRM Data].[dbo].[ID_Address_Consent] IAC ON PL.[TaxId] = IAC.[Tax ID]"
            "WHERE UserId = '"+ userid + "'"
            )
            resultset = conn.execute(qry)
            results_as_dict = resultset.mappings().all()
            if len(results_as_dict) == 0:
                noneKIS = 'ไม่สามารถใช้ฟังก์ชันนี้ได้ เนื่องจากรถของคุณไม่ได้ติด KIS'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=noneKIS))
            else:
                CallButtonJson = []
                for i in results_as_dict:
                    VIN = i['VIN']
                    CallButtonJson.append(CallButtonSelectByVINHistory(VIN))
                flex_message = callButtonBody(CallButtonJson)
                line_bot_api.reply_message(event.reply_token,flex_message)
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/register', methods=['GET','POST'])
def register():
    print('Request for index page received')
    return render_template('register.html')

@app.route('/insert_register', methods=['GET','POST'])
def insert_register():
    taxId = request.form.get('taxId')
    userId = request.form.get('userId')
    displayName = request.form.get('displayName')
    pictureUrl = request.form.get('pictureUrl')
    createTime = datetime.today()
    createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
    status = '200'
    id = os.urandom(16).hex()
    #check taxid
    con = ConnectDB('CRM Data')
    with con.begin() as conn:
        qry = sa.text("SELECT [Tax ID] FROM [CRM Data].[dbo].[ID_Address_Consent] "
        "WHERE [Tax ID] = '"+ taxId +"'"
        "ORDER BY [Tax ID] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
        )
        resultset = conn.execute(qry)
        results_as_dict = resultset.mappings().all()
    df = pd.DataFrame.from_dict(results_as_dict)
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
        if len(df)==0:
            flash("ไม่พบเลขบัตรประจำตัวประชาชนหรือเลขทะเบียนนิติบุคคล")
            # return render_template('register.html', flash_message="True")
            return redirect(url_for('register'))
        elif len(dfLine)!=0:
            flash("คุณได้ทำการลงทะเบียนแล้ว")
            return redirect(url_for('register'))
        else:
            con = ConnectDB('Line Data')
            with con.begin() as conn:
                insertData = sa.text("INSERT INTO [Line Data].[dbo].[Profile Line] "
                "([ProfileId], [Status], [Name], [Image], [UserId], [TaxId], [CreateTime])"
                "VALUES"
                "('"+ id +"','"+ status +"','"+ displayName +"','"+ pictureUrl +"','"+ userId +"','"+ taxId +"','"+ createTime +"')"
                )
                resultsetInsertData = conn.execute(insertData)
            flash("ลงทะเบียนแล้วเรียบร้อย")
            url = 'https://api.line.me/v2/bot/user/'+userId+'/richmenu/richmenu-a7aebafbb2615ba2b2ab8b6932429e11'
            headers = {'content-type': 'application/json','Authorization':'Bearer J9o+1YH2mYc/4RiFFOjgXTYqCIxT//ctqWgLjB4kyYlw8qaieSnNl42uyn/TMfk7PuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIRkiDDAVQ0PKiz2wreUTFBG4Vpv+hDtLSk1QAnu2V2pOwdB04t89/1O/w1cDnyilFU='}
            r = requests.post(url, headers=headers)
            return render_template('insert_register.html')

@app.route('/history', methods=['GET','POST'])
def history():
    VIN = request.args.get('VIN')
    con = ConnectDB('Service Data')
    with con.begin() as conn:
        qry = sa.text("SELECT [VIN],[Vehicle Type Text],[LV Main Type],[Billing Date],[Billing Created On],[Symptom],[Net Value]"
        "FROM [Service Data].[dbo].[Service_Header]"
        "WHERE [VIN] = '"+ VIN +"'"
        "ORDER BY [Billing Date] DESC"
        )
        resultset = conn.execute(qry)
        data = resultset.mappings().all()
    return render_template('history.html', data=data)

if __name__ == "__main__":
    app.run()