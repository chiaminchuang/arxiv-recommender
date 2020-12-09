from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import logging
from typing import List, Dict

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ES_HOST, \
    AWS_ES_REGION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('aws-api')


# TODO: use a decorator to check whether document is a valid arxiv paper.

class ESEngine:
    """ Wrapper for Elasticsearch

    Attritubes:
        es: elasticsearch client
        sort: sorting methods 
    """

    def __init__(self):
        service = 'es'
        awsauth = AWS4Auth(
            AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ES_REGION, service)

        self.es = Elasticsearch(
            hosts=[{'host': AWS_ES_HOST, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        self.sort = [
            "_score",
            {
                "date": {
                    "order": "asc"
                }
            }
        ]

        logger.info(self.es.info())

    # def es_index(self, doc):

    #     self.es.index(index="arxiv", doc_type="doc", body=doc)
    #     logger.info(self.es.get(index="arxiv", doc_type="doc"))

    def index_bulk(self, docs: List[Dict]) -> None:
        """
        Args:
            docs:

        """

        if not docs:
            logger.warning(f'Cannot index empty document. docs: `{docs}`')

        body = []
        for doc in docs:
            body.append({'index': {'_index': 'arxiv'}})
            body.append(doc)

        res = self.es.bulk(doc_type='doc', body=body)
        logger.info(res)

    def search(
            self, query: str, fields: List[str] = ['abstract'],
            size: int = 5) -> List[Dict]:
        """
        Args:
            query: ex: 'summarization'
            fields: ex: ['title', 'abstract']
            size: 

        Returns:

        """
        # https://www.cnblogs.com/ExMan/p/11323984.html
        # match_all = {"match_all": {}}
        multi_match = {'multi_match': {'query': query, 'fields': fields}}

        body = {
            'query': multi_match,
            "sort": self.sort
        }
        res = self.es.search(index='arxiv', body=body, size=size)
        res = res['hits']['hits']

        return res

    def search_by_arxiv_id(self, arxiv_id: str) -> Dict:
        """ 
        Args:
            arxiv_id: ex: 2012.03930

        Returns:
            res
        """

        res = self.search(query=arxiv_id, fields=['arxiv_id'])

        assert len(res) == 1, res

        return res[0]

    def update(self, doc: Dict, doc_id: str = '', arxiv_id: str = ''):
        """
        Args:
            doc: {'field1': value1, 'field2': value2}
        """

        if not doc:
            logger.warning(f'Cannot update empty document. doc: {doc}')

        if not doc_id:
            # if doc_id is not provided, get doc_id by `search_by_arxiv_id`
            assert arxiv_id
            doc_id = self.search_by_arxiv_id(arxiv_id)['_id']

        body = {'doc': doc}
        self.es.update(index='arxiv', doc_type='doc', id=doc_id, body=body)

    def delete_all(self) -> None:
        """ Delete all the documents in index `arxiv`
        """
        self.es.indices.delete(index='arxiv')


# es = ESEngine()

# es
        # es = es_connect()
        # es_delete(es)

        # es = es_connect()
        # keyword = "summarization"
        # papers = recommand_randomly(keyword)
        # papers = [p.get_json() for p in papers]
        # es_index_bulk(es, papers)
        # es_search(es)
