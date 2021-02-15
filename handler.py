import logging
import json
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import FlexSendMessage, TextSendMessage
from linebot.exceptions import LineBotApiError

from settings import CHANNEL_ACCESS_TOKEN, CHANNEL_SECRET, USER_ID
from src.aws_api import ESEngine
from src.paper import Paper

es = ESEngine()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('lambda-handler')


def weekly_papers(event, context):
    print(event)
    print(context)

    linebot = LineBotApi(CHANNEL_ACCESS_TOKEN)

    papers = es.random_search(size=5)
    papers = [Paper(json=p) for p in papers]

    contents = {'type': 'carousel', 'contents': [
                p.get_flex_contents() for p in papers]}

    try:
        linebot.push_message(USER_ID, FlexSendMessage(
            alt_text='Weekly Papers',
            contents=contents
        ))
    except LineBotApiError as e:
        print(e)


def webhook(event, context):
    # receive user input

    linebot = LineBotApi(CHANNEL_ACCESS_TOKEN)
    # handler = WebhookHandler(CHANNEL_SECRET)

    # msg = json.loads(event['body'])

    # {"events":[
    #   {"type":"message","replyToken":"a5d6dadb84a346428bc53ea9ce656cea", "message":{"type":"text","id":"13044610237128","text":"yo"}}
    # ]}
    events = json.loads(event['body'])['events']
    for e in events:
        reply_token = e['replyToken']
        text = e['message']['text'].strip()

        papers = es.search(text, ['title', 'abstract'])
        papers = [Paper(json=p) for p in papers]

        if papers:
            contents = {'type': 'carousel', 'contents': [
                p.get_flex_contents() for p in papers]}

            linebot.reply_message(reply_token, FlexSendMessage(
                alt_text=f'papers for {text}',
                contents=contents
            ))
        else:
            linebot.reply_message(reply_token,
                                  TextSendMessage(text='Results Not Found'))

    response = {
        'statusCode': 200,
        'body': json.dumps({'message': 'ok'})
    }

    return response


# if __name__ == '__main__':
#     push()
