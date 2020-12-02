import requests
from bs4 import BeautifulSoup
from paper import Paper

# sortBy: ['lastUpdatedDate', 'submittedDate']
# sortOrder: ['descending', 'ascending']
BASE_URL = 'http://export.arxiv.org/api/query?search_query={}&start={}&max_results={}&sortBy=submittedDate&sortOrder=descending'

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


def preprocess_params(url_func):
    # query: 'summarization,machine translation'
    # ret: ['summarization', 'machine+translation']

    def _process(query, **kwargs):
        query = query.split(',')
        query = [q.strip().replace(' ', '+') for q in query]
        return url_func(query, **kwargs)

    return _process


@preprocess_params
def construct_url(query, id_list=None, start=0, max_results=5):

    ti = LEFT_PARENS + '+OR+'.join(['ti:' + q for q in query]) + RIGHT_PARENS
    abs = LEFT_PARENS + \
        '+AND+'.join(['abs:' + q for q in query]) + RIGHT_PARENS

    cat = LEFT_PARENS + '+OR+'.join(['cat:' + c for c in CAT]) + RIGHT_PARENS

    search_query = f'{LEFT_PARENS}{ti}+OR+{abs}{RIGHT_PARENS}+AND+{cat}'
    # search_query = f'{ti}+OR+{abs}+AND+{cat}'

    url = BASE_URL.format(search_query, start, max_results)

    if id_list:
        url += "&id_list=" + ','.join(id_list)

    print(url)
    return url


def recommand_randomly(query):

    url = construct_url(query, max_results=3)
    res = requests.get(url).content

    soup = BeautifulSoup(res, 'html.parser')

    papers = [Paper(entry) for entry in soup.findAll('entry')]

    return papers


# recommand_randomly('summarization')


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


# Vespa


# curl -XPUT -u 'eddie:#Ce140207' 'https://search-arxivrecommender-kqwfiyazbtaxiqupo6zif24pnq.us-east-2.es.amazonaws.com/movies/_doc/1' -d '{"director": "Burton, Tim", "genre": ["Comedy","Sci-Fi"], "year": 1996, "actor": ["Jack Nicholson","Pierce Brosnan","Sarah Jessica Parker"], "title": "Mars Attacks!"}' -H 'Content-Type: application/json'
