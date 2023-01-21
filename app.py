from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,FlexSendMessage
)
from buttonLine import *

app = Flask(__name__)

line_bot_api = LineBotApi('J9o+1YH2mYc/4RiFFOjgXTYqCIxT//ctqWgLjB4kyYlw8qaieSnNl42uyn/TMfk7PuWAe9S8hyL5JDIA00Vfr24Ltdq+97ds4BNk4htsAIRkiDDAVQ0PKiz2wreUTFBG4Vpv+hDtLSk1QAnu2V2pOwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7f9e03908fca984853b2fc322c1775c6')

def ConnectDB(db,table):
    #configure sql server
    server = '172.31.8.25'
    database =  db
    username = 'boon'
    password = 'Boon@DA123'
    driver = '{ODBC Driver 17 for SQL Server}'
    dsn = 'DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password
    params = urllib.parse.quote_plus(dsn)
    engine = sa.create_engine('mssql+pyodbc:///?odbc_connect=%s' % params)
    connection = engine.connect()
    metadata = sa.MetaData()
    tablename = sa.Table(table, metadata, autoload=True, autoload_with=engine)
    query = sa.select([tablename])
    ResultProxy = connection.execute(query)
    ResultSet = ResultProxy.fetchall()
    LineSelectUser = pd.DataFrame(ResultSet)
    return LineSelectUser

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
        LineSelectUser = ConnectDB('Line Data','Profile Line')
        LineSelectUser = LineSelectUser.query('UserId == "Ud41fb829bb1e5220c1d2b39fb366996b"')
        nameF = LineSelectUser['Name'].values[0]
        # flex_message = Allvalue(nameF)
        # line_bot_api.reply_message(event.reply_token,flex_message)
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(nameF=event.message.text))
    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run()