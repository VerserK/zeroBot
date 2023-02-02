from flask import Flask, request, abort

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
import datetime
from buttonLine import *
import sqlalchemy as sa
import urllib

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
                Unregis = 'ไม่สามารใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
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
                    Model = i['Model']
                    VIN = i['VIN']
                    UsageHour = i['Usage Hours']
                    SaleDate = i['Sale Date'].strftime("%d %B, %Y")
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
            Unregis = 'ไม่สามารใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
            mainA(userid)
        else:
            mainB(userid)
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

# @handler.add(FollowEvent)
# def handle_follow(event):
#     profile = line_bot_api.get_profile(event.source.user_id)
#     userid = profile.user_id
#     print(userid)
#     con = ConnectDB('Line Data')
#     with con.begin() as conn:
#         qry = sa.text("SELECT Name,TaxId,UserId FROM [Line Data].[dbo].[Profile Line] PL "
#         "WHERE UserId = '" + userid + "'"
#         "ORDER BY [UserId] OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY"
#         )
#         resultset = conn.execute(qry)
#         results_as_dict = resultset.mappings().all()
#     if len(results_as_dict)==0:
#         Unregis = 'ไม่สามารใช้งานได้เนื่องจากคุณยังไม่ลงทะเบียน'
#         line_bot_api.reply_message(event.reply_token, TextSendMessage(text=Unregis))
#         mainA()
#     else:
#         mainB()

def mainA(user_id):
    rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="richmenu A",
    chat_bar_text="เปิดเมนู",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=837),
        action=URIAction(label='Go to line.me', uri='https://zerosearch.azurewebsites.net/auth/register.php')),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ดูข้อมูลรถทั้งหมด')),
        RichMenuArea(
        bounds=RichMenuBounds(x=847, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ค้นหารถ')),
        RichMenuArea(
        bounds=RichMenuBounds(x=1688, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ประวัติบริการ'))
        ]
    )
    rich_menu_id_a = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    # 5. Upload image to rich menu A
    with open('./public/1.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id_a, 'image/png', f)

    #6. Set rich menu A as the default rich menu
    line_bot_api.link_rich_menu_to_users(user_id, rich_menu_id_a)

    print('success A')

def mainB(user_id):
    rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="richmenu B",
    chat_bar_text="เปิดเมนู",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=837),
        action=URIAction(label='Go to line.me', uri='https://korp.siamkubota.co.th/Customer/index_login.php')),
        RichMenuArea(
        bounds=RichMenuBounds(x=0, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ดูข้อมูลรถทั้งหมด')),
        RichMenuArea(
        bounds=RichMenuBounds(x=847, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ค้นหารถ')),
        RichMenuArea(
        bounds=RichMenuBounds(x=1688, y=842, width=812, height=844),
        action=MessageAction(type='message' ,label='Go to line.me', text='ประวัติบริการ'))
        ]
    )
    rich_menu_id_b = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print(rich_menu_id_b)

    # 5. Upload image to rich menu B
    with open('./public/2a.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id_b, 'image/png', f)

    #6. Set rich menu A as the default rich menu
    # line_bot_api.set_default_rich_menu(rich_menu_id_b)
    line_bot_api.link_rich_menu_to_users(user_id, rich_menu_id_b)

    print('success B')

def mainC():
    rich_menu_to_create = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name="richmenu B",
    chat_bar_text="เปิดเมนู",
    areas=[RichMenuArea(
        bounds=RichMenuBounds(x=0, y=0, width=2500, height=1686),
        action=MessageAction(type='message' ,label='Go to line.me', text='เข้าสู่ระบบ'))
        ]
    )
    rich_menu_id_c = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    # 5. Upload image to rich menu B
    with open('./public/richmenu-a.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id_c, 'image/png', f)

    #6. Set rich menu A as the default rich menu
    line_bot_api.set_default_rich_menu(rich_menu_id_c)

    rich_menu_list = line_bot_api.get_rich_menu_list()
    for rich_menu in rich_menu_list:
        print(rich_menu.rich_menu_id)

    print('success C')

mainC()

if __name__ == "__main__":
    app.run()