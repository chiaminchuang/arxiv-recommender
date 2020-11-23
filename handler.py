import json
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)

from settings import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET
from arxiv_api import recommand_randomly


def webhook(event, context):
    # receive user input

    linebot = LineBotApi(CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(CHANNEL_SECRET)

    msg = json.loads(event['body'])

    query = msg['events'][0]['message']['text']
    papers = recommand_randomly(query)

    # {"events":[
    #   {"type":"message","replyToken":"a5d6dadb84a346428bc53ea9ce656cea", "message":{"type":"text","id":"13044610237128","text":"yo"}}
    # ]}
    reply_token = msg['events'][0]['replyToken']

    contents = {'type': 'carousel', 'contents': [
        p.get_flex_contents() for p in papers]}

    linebot.reply_message(reply_token, FlexSendMessage(
        alt_text='hello',
        contents=contents
    ))

    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'ok'})
    }

    return response
