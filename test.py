import os
import sys

from linebot import (
    LineBotApi,
)

from linebot.models import (
    RichMenu,
    RichMenuArea,
    RichMenuSize,
    RichMenuBounds,
    URIAction
)
from linebot.models.actions import RichMenuSwitchAction
from linebot.models.rich_menu import RichMenuAlias

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)


def rich_menu_object_a_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-a",
        "chatBarText": "Tap to open",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "uri",
                    "uri": "https://www.line-community.me/"
                }
            },
            {
                "bounds": {
                    "x": 1251,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-b",
                    "data": "richmenu-changed-to-b"
                }
            }
        ]
    }


def rich_menu_object_b_json():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "richmenu-b",
        "chatBarText": "Tap to open",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "richmenuswitch",
                    "richMenuAliasId": "richmenu-alias-a",
                    "data": "richmenu-changed-to-a"
                }
            },
            {
                "bounds": {
                    "x": 1251,
                    "y": 0,
                    "width": 1250,
                    "height": 1686
                },
                "action": {
                    "type": "uri",
                    "uri": "https://www.line-community.me/"
                }
            }
        ]
    }


def create_action(action):
    if action['type'] == 'uri':
        return URIAction(type=action['type'], uri=action.get('uri'))
    else:
        return RichMenuSwitchAction(
            type=action['type'],
            rich_menu_alias_id=action.get('richMenuAliasId'),
            data=action.get('data')
        )


def main():
    # 2. Create rich menu A (richmenu-a)
    rich_menu_object_a = rich_menu_object_a_json()
    areas = [
        RichMenuArea(
            bounds=RichMenuBounds(
                x=info['bounds']['x'],
                y=info['bounds']['y'],
                width=info['bounds']['width'],
                height=info['bounds']['height']
            ),
            action=create_action(info['action'])
        ) for info in rich_menu_object_a['areas']
    ]

    rich_menu_to_a_create = RichMenu(
        size=RichMenuSize(width=rich_menu_object_a['size']['width'], height=rich_menu_object_a['size']['height']),
        selected=rich_menu_object_a['selected'],
        name=rich_menu_object_a['name'],
        chat_bar_text=rich_menu_object_a['name'],
        areas=areas
    )

    rich_menu_a_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_a_create)

    # 3. Upload image to rich menu A
    with open('./public/richmenu-a.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_a_id, 'image/png', f)

    # 4. Create rich menu B (richmenu-b)
    rich_menu_object_b = rich_menu_object_b_json()
    areas = [
        RichMenuArea(
            bounds=RichMenuBounds(
                x=info['bounds']['x'],
                y=info['bounds']['y'],
                width=info['bounds']['width'],
                height=info['bounds']['height']
            ),
            action=create_action(info['action'])
        ) for info in rich_menu_object_b['areas']
    ]

    rich_menu_to_b_create = RichMenu(
        size=RichMenuSize(width=rich_menu_object_b['size']['width'], height=rich_menu_object_b['size']['height']),
        selected=rich_menu_object_b['selected'],
        name=rich_menu_object_b['name'],
        chat_bar_text=rich_menu_object_b['name'],
        areas=areas
    )

    rich_menu_b_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_b_create)

    # 5. Upload image to rich menu B
    with open('./public/richmenu-b.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_b_id, 'image/png', f)

    # 6. Set rich menu A as the default rich menu
    line_bot_api.set_default_rich_menu(rich_menu_b_id)

    # 7. Create rich menu alias A
    alias_a = RichMenuAlias(
        rich_menu_alias_id='richmenu-alias-a',
        rich_menu_id=rich_menu_a_id
    )
    line_bot_api.create_rich_menu_alias(alias_a)

    # 8. Create rich menu alias B
    alias_b = RichMenuAlias(
        rich_menu_alias_id='richmenu-alias-b',
        rich_menu_id=rich_menu_b_id
    )
    line_bot_api.create_rich_menu_alias(alias_b)
    print('success')


    {
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