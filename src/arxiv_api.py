import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import logging
import time
# import json
# import argparse
from typing import Callable, List, Dict

# from src.aws_api import ESEngine
from src.paper import Paper

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


def preprocess_params(url_func: Callable):
    # query: 'summarization,machine translation'
    # ret: ['summarization', 'machine+translation']

    def _process(obj, query: str, **kwargs):
        query = query.lower().split(',') if query else []
        query = [q.strip().replace(' ', '+') for q in query]
        return url_func(obj, query, **kwargs)

    return _process


class ArxivSearch:
    """ Wrapper for arxiv search engine api

    Attritubes:
        sleep (int): 
        chunk_size (int):
        sortBy (str):
        sortOrder (str):

    """

    def __init__(
            self, sortBy: str = 'submittedDate', sortOrder: str = 'descending'):
        """
        Args:
            sortBy:
            sortOrder:  
        """
        self.sleep = 3
        self.max_timeout = 10
        self.chunk_size = 1000
        self.sortBy = sortBy
        self.sortOrder = sortOrder

    def get_total_results(self, query: str) -> int:
        """
        Args:
            query:

        Returns:
            The number of the total results in the query.
        """
        url = self.construct_url(query, start=0, max_results=1)
        res = requests.get(url).content
        soup = BeautifulSoup(res, 'html.parser')

        return int(soup.find('opensearch:totalresults').string)

    def _process_results(self, url: str) -> List[Dict]:

        res = requests.get(url).content
        soup = BeautifulSoup(res, 'html.parser')
        papers = [Paper(entry=entry) for entry in soup.findAll('entry')]

        return [p.get_json() for p in papers]

    @preprocess_params
    def construct_url(
            self, query: List[str],
            start: int = 0, max_results: int = 0) -> str:

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

        return url

    def search(self, query: str, max_results: int) -> List[Dict]:

        total = self.get_total_results(query)
        logger.info(f'The number of the total results is {total}')

        if max_results == -1:
            max_results = total
        max_results = min(max_results, total)

        papers = []
        logger.info(
            f'Attempt to retrieve papers from arXiv. (query=`{query}`, max_results={max_results})')

        timeout = 0
        while len(papers) < max_results:
            t = time.time()

            n_results = min(max_results, self.chunk_size) \
                if max_results != -1 else self.chunk_size
            start = len(papers)

            url = self.construct_url(query, start=start, max_results=n_results)
            logger.info(url)

            _papers = self._process_results(url)

            logger.info(
                f'Retrieved {len(_papers)} papers in {time.time()-t:.2f} sec. (start={start}, n_results={n_results})\n')

            if _papers:
                papers.extend(_papers)
                timeout = 0  # Reset timeout
            elif timeout == self.max_timeout:
                logger.info('Exceeded maximum timeout and stopped retrieving.')
                break
            else:
                # Retrieved 0 papers. Retry.
                timeout += 1
                logger.info(f'Retry {timeout} time(s).')

            time.sleep(self.sleep)

        papers = papers[:max_results] if max_results != -1 else papers
        logger.info(f'Retrieved {len(papers)} papers in total.')
        return papers


# if __name__ == '__main__':

#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '--query', type=str, default='',
#         help='Search query for arxiv paper. Use `,` as separator for multiple query')
#     parser.add_argument('--n', type=int, default=10,
#                         help='The number of returned results')

#     args = parser.parse_args()
#     arxiv = ArxivSearch()
#     papers = arxiv.search(args.query, args.n)

    # es = ESEngine()
    # es.delete_all()
    # es.index_bulk(papers)

    # res = es.search_by_arxiv_id('2012.04623')
    # print(res)

    # res = es.search('')
    # for r in res:
    #     print(r, end='\n\n')

    # es.update(
    #     {'comment': 'commented updated', 'category': ['xxx']},
    #     arxiv_id='2012.04623')

    # res = es.search_by_arxiv_id('2012.04623')
    # print(res)

    # with open('papers.json', 'w') as f:
    #     json.dump(papers, f)
