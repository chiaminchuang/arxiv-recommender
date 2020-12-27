import json
import requests
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)

from settings import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET
from aws_api import ESEngine
from paper import Paper

es = ESEngine()


def webhook(event, context):
    # receive user input

    linebot = LineBotApi(CHANNEL_ACCESS_TOKEN)
    # handler = WebhookHandler(CHANNEL_SECRET)

    msg = json.loads(event['body'])

    query = msg['events'][0]['message']['text']
    papers = es.search(query, ['title', 'abstract'])
    papers = [Paper(json=p) for p in papers]

    # {"events":[
    #   {"type":"message","replyToken":"a5d6dadb84a346428bc53ea9ce656cea", "message":{"type":"text","id":"13044610237128","text":"yo"}}
    # ]}
    reply_token = msg['events'][0]['replyToken']

    contents = {'type': 'carousel', 'contents': [
        p.get_flex_contents() for p in papers]}

    linebot.reply_message(reply_token, FlexSendMessage(
        alt_text=f'papers for {query}',
        contents=contents
    ))

    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'ok'})
    }

    return response
