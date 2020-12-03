import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import logging
import time

from paper import Paper

# sortBy: ['relevance', 'lastUpdatedDate', 'submittedDate']
# sortOrder: ['descending', 'ascending']
# BASE_URL = 'http://export.arxiv.org/api/query?search_query={}&start={}&max_results={}&sortBy=submittedDate&sortOrder=descending'
BASE_URL = 'http://export.arxiv.org/api/query?'

# arxiv api document
# https://arxiv.org/help/api/user-manual#query_details

# Subject Classifications / Categories
# cs.AI -> Artificial Intelligence
# cs.LG -> Machine Learning
# cs.CL -> Computation and Language
# cs.CV -> Computer Vision and Pattern Recongnition
# cs.IR -> Information Retrieval
CAT = ['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.IR']
# LEFT_PARENS = '%28'
# RIGHT_PARENS = '%29'
# DOUBLE_QUOTE = '%22'
LEFT_PARENS = '('
RIGHT_PARENS = ')'
DOUBLE_QUOTE = '"'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('arxiv-api')


def preprocess_params(url_func):
    # query: 'summarization,machine translation'
    # ret: ['summarization', 'machine+translation']

    def _process(obj, query, **kwargs):
        query = query.lower().split(',') if query else []
        query = [q.strip().replace(' ', '+') for q in query]
        return url_func(obj, query, **kwargs)

    return _process


class ArxivSearch:
    def __init__(self, sortBy='submittedDate', sortOrder='descending'):

        self.sleep = 3
        self.chunck_size = 1000
        self.sortBy = sortBy
        self.sortOrder = sortOrder

    def _process_results(self, res):

        soup = BeautifulSoup(res, 'html.parser')
        papers = [Paper(entry=entry) for entry in soup.findAll('entry')]

        return [p.get_json() for p in papers]

    @preprocess_params
    def construct_url(self, query, start=0, max_results=5):

        if query:
            ti = [f'ti:{q}' for q in query]
            ti = LEFT_PARENS + ' OR '.join(ti) + RIGHT_PARENS

        if query:
            ab = [f'abs:{q}' for q in query]
            ab = LEFT_PARENS + ' AND '.join(ab) + RIGHT_PARENS

        cat = [f'cat:{c}' for c in CAT]
        cat = LEFT_PARENS + ' OR '.join(cat) + RIGHT_PARENS

        search_query = f'{LEFT_PARENS}{ti} OR {ab}{RIGHT_PARENS} AND {cat}' \
            if query else cat

        args = {
            'search_query': search_query,
            'start': start,
            'max_results': max_results,
            'sortBy': self.sortBy,
            'sortOrder': self.sortOrder
        }

        url = BASE_URL + urlencode(args)

        logger.info(url)
        return url

    def search(self, query, max_results):

        papers = []
        logger.info(
            f'Attempt to retrieve papers from arXiv. (query=`{query}`, max_results={max_results})')
        while len(papers) < max_results:
            t = time.time()
            n_results = min(max_results, self.chunck_size) \
                if max_results != -1 else self.chunck_size
            start = len(papers)

            url = self.construct_url(query, start=start, max_results=n_results)
            res = requests.get(url).content

            _papers = self._process_results(res)
            if not _papers:
                break

            papers.extend(_papers)
            logger.info(
                f'Retrieve {len(_papers)} papers in {time.time()-t:.2f} sec. (start={start}, n_results={n_results})\n')

        papers = papers[:max_results] if max_results != -1 else papers
        logger.info(f'Retrieved {len(papers)} papers in total.')
        return papers

# def recommand_randomly(query):

#     url = construct_url(query, max_results=3)
#     res = requests.get(url).content

#     soup = BeautifulSoup(res, 'html.parser')

#     papers = [Paper(entry) for entry in soup.findAll('entry')]

#     return papers


arxiv = ArxivSearch()
arxiv.search('', 5000)


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
