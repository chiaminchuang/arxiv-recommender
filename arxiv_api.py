import requests
from bs4 import BeautifulSoup
from paper import Paper

# sortBy: ['lastUpdatedDate', 'submittedDate']
BASE_URL = 'http://export.arxiv.org/api/query?search_query={}&start={}&max_results={}&sortBy=submittedDate&sortOrder=ascending'

# arxiv api document
# https://arxiv.org/help/api/user-manual#query_details

# Subject Classifications / Categories
# cs.AI -> Artificial Intelligence
# cs.LG -> Machine Learning
# cs.CL -> Computation and Language
# cs.CV -> Computer Vision and Pattern Recongnition
# cs.IR -> Information Retrieval
CAT = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.IR']
LEFT_PARENS = '%28'
RIGHT_PARENS = '%29'
DOUBLE_QUOTE = '%22'


def construct_url(query, id_list=None, start=0, max_results=5):
    ti = LEFT_PARENS + '+OR+'.join(['ti:' + q for q in query]) + RIGHT_PARENS
    abs = LEFT_PARENS + \
        '+AND+'.join(['abs:' + q for q in query]) + RIGHT_PARENS

    cat = LEFT_PARENS + '+OR+'.join(['cat:' + c for c in CAT]) + RIGHT_PARENS

    search_query = ti + '+OR+' + '+AND+'.join([abs, cat])

    url = BASE_URL.format(search_query, start, max_results)

    if id_list:
        url += "&id_list=" + ','.join(id_list)

    return url


def recommand_randomly(query):

    url = construct_url(query)
    res = requests.get(url).content

    soup = BeautifulSoup(res, 'html.parser')

    papers = [Paper(entry) for entry in soup.findAll('entry')]

    return papers


# 1. get user interests from mysql (create a interest table for each user)
# 2. use user interests as keywords to search papers through arxiv api
# 3. send papers messages to SQS
# 4. SQS trigger Lambda
# 5. Lambda send papers message to LINE user through LINE Notify

# 6. get feedback or new interests from user
# 7. update mysql data


# Lambda 1: send papers to users
# Lambda 2: send user interests to mysql
# SQS 1: receive arxiv.api results and send them Lambda 1
# SQS 2: receive user inputs from linebot and send them to Lambda 2

# Usecase - Recommend automatically:
# arxiv.api (crontab) -> SQS 1 -> Lambda 1 -> user line

# Usecase - Update User info:
# User line inputs -> SQS 2 -> Lambda 2 -> mysql


# {
#   "type": "carousel",
#   "contents": [
#     {
#       "type": "bubble",
#       "header": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "text",
#             "text": "Unsupervised Text Style Transfer using Language Models as Discriminators",
#             "size": "md",
#             "weight": "bold"
#           }
#         ]
#       },
#       "hero": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "text",
#             "text": "Zichao Yang, Zhiting Hu, Chris Dyer, Eric P. Xing, Taylor Berg-Kirkpatrick",
#             "size": "xxs",
#             "style": "italic",
#             "margin": "none",
#             "offsetStart": "xxl"
#           }
#         ]
#       },
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "text",
#             "text": "Binary classifiers are often employed as discriminators in GAN-based unsupervised style transfer systems to ensure that transferred sentences are similar to sentences in the target domain. One difficulty with this approach is that the error signal provided by the discriminator can be unstable and is sometimes insufficient to train the generator to produce fluent language.",
#             "wrap": true,
#             "size": "sm",
#             "offsetEnd": "none"
#           }
#         ],
#         "margin": "none"
#       },
#       "footer": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": [
#           {
#             "type": "box",
#             "layout": "vertical",
#             "contents": [
#               {
#                 "type": "text",
#                 "text": "NeurIPS camera ready",
#                 "size": "xs",
#                 "style": "italic",
#                 "wrap": true,
#                 "offsetStart": "md"
#               },
#               {
#                 "type": "text",
#                 "text": "2018-05",
#                 "size": "xs",
#                 "style": "italic",
#                 "offsetStart": "md"
#               },
#               {
#                 "type": "spacer"
#               }
#             ]
#           },
#           {
#             "type": "button",
#             "action": {
#               "type": "uri",
#               "label": "Study",
#               "uri": "http://linecorp.com/"
#             },
#             "offsetTop": "none",
#             "offsetBottom": "none",
#             "height": "sm",
#             "style": "primary"
#           }
#         ]
#       },
#       "styles": {
#         "footer": {
#           "separator": false
#         }
#       }
#     },
#     {
#       "type": "bubble",
#       "body": {
#         "type": "box",
#         "layout": "vertical",
#         "contents": []
#       }
#     }
#   ]
# }
