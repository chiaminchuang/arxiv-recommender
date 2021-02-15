from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError
from requests_aws4auth import AWS4Auth
import logging
import random
from typing import List, Dict

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ES_HOST, \
    AWS_ES_REGION

# from src.paper import Paper

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

    def index(self, doc):
        self.es.index(index="arxiv", doc_type="doc", id="123", body=doc)

        # logger.info(self.es.get(index="arxiv", doc_type="doc"))

    def index_bulk(self, docs: List[Dict]) -> None:
        """
        Args:
            docs: a list of document

        Returns:
            None

        Example:
            papers = [{
              "arxiv_id": "2012.13253",
              "link": "http://arxiv.org/abs/2012.13253v1",
              "title": "Soft-IntroVAE...",
              "abstract": "The recently introduced introspective variational autoencoder ...",
              "category": ["cs.LG", "cs.AI", "cs.CV"],
              "date": "2020-12"}, ...]

            es = ESEngine()
            es.index_bulk(papers)
        """

        if not docs:
            logger.warning(f'Cannot index empty document. docs: `{docs}`')

        # n_new, n_update = 0, 0
        total = 0
        body = []
        # for doc in docs:
        #     body.append({'index': {'_index': 'arxiv', "_id": doc['arxiv_id']}})
        #     body.append(doc)

        for doc in docs:
            # res = self.search_by_arxiv_id(doc['arxiv_id'])
            # if res:
            #     logger.info(
            #         f"The doc with the arxiv_id `{doc['arxiv_id']}` exists. Updating it.")
            #     self.update(doc, doc_id=res['_id'])
            #     n_update += 1
            # else:
            # body.append({'index': {'_index': 'arxiv', "_id": doc['arxiv_id']}})
            body.append({'index': {'_index': 'arxiv', "_id": str(total)}})
            body.append(doc)
            total += 1
            if len(body) // 2 >= 1000:
                logger.info(f"Batch indexing {len(body) // 2} new docs.")
                # n_new += len(body) // 2
                self.es.bulk(doc_type='doc', body=body)
                body = []

        if body:
            logger.info(f"Batch indexing {len(body) // 2} new docs.")
            self.es.bulk(doc_type='doc', body=body)

        # n_new += len(body) // 2
        logger.info(f"Summary: Indexed {total} docs.")

    def random_search(self, size=5):
        """
        Args:
            size: result size

        Returns:
            [{
              "arxiv_id": "2012.13253",
              "link": "http://arxiv.org/abs/2012.13253v1",
              "title": "Soft-IntroVAE...",
              "abstract": "The recently introduced introspective variational autoencoder ...",
              "category": ["cs.LG", "cs.AI", "cs.CV"],
              "date": "2020-12"}, ...]

        Example:
          es = ESEngine()
          es.random_search(size=5)
        """

        body = {
            'query': {
                "function_score": {
                    "functions": [
                        {
                            "random_score": {
                                "seed": str(random.randint(0, 2**16))
                            }
                        }
                    ]
                }
            },
            'sort': self.sort
        }

        try:
            res = self.es.search(index='arxiv', body=body, size=size)
        except NotFoundError as err:
            logger.error(err)
            # index_not_found_exception, no such index `arxiv`
            return []

        # check the example_es_search_response.json for returned details
        res = res['hits']['hits']

        res = [{'_id': r['_id'], **r['_source']} for r in res]

        return res

    def search(
            self, query: str, fields: List[str] = ['abstract'],
            size: int = 5) -> List[Dict]:
        """
        Args:
            query: keyword to serach, ex: 'summarization'
            fields: fields to search, ex: ['title', 'abstract']
            size: result size

        Returns:
            [{
              "arxiv_id": "2012.13253",
              "link": "http://arxiv.org/abs/2012.13253v1",
              "title": "Soft-IntroVAE...",
              "abstract": "The recently introduced introspective variational autoencoder ...",
              "category": ["cs.LG", "cs.AI", "cs.CV"],
              "date": "2020-12"}, ...]

        Example:
          es = ESEngine()
          es.search('summarization', fields=['title', 'abstract'], size=2)
        """
        # https://www.cnblogs.com/ExMan/p/11323984.html
        match_all = {"match_all": {}}
        # multi_match = {'multi_match': {'query': query,
        #                                'fields': fields}}  # "operator": "and"

        body = {
            'query': match_all,
            # 'query': multi_match,

            'sort': self.sort,
            # 'fields': '*',
        }

        try:
            res = self.es.search(index='arxiv', body=body, size=size)
        except NotFoundError as err:
            logger.error(err)
            # index_not_found_exception, no such index `arxiv`
            return []

        # check the example_es_search_response.json for returned details
        res = res['hits']['hits']

        res = [{'_id': r['_id'], **r['_source']} for r in res]

        return res

    def search_by_arxiv_id(self, arxiv_id: str) -> Dict:
        """
        Args:
            arxiv_id: arxiv paper id, ex: 2012.03930

        Returns:
            res
        """

        res = self.search(query=arxiv_id, fields=['arxiv_id'])

        if len(res) > 1:
            logger.warning(
                f"There are {len(res)} duplicate documents for arxiv_id `{arxiv_id}`. Return the first one.")

        return res[0] if res else None

    def is_exist(self, arxiv_id: str) -> bool:
        """
        Args:
            arxiv_id: arxiv paper id, ex: 2012.03930

        Returns:
            return True if the doc with the given arxiv_id exists, otherwise, return False
        """
        return self.search_by_arxiv_id(arxiv_id) is not None

    def update(self, doc: Dict, arxiv_id: str) -> None:
        """
        Args:
            doc: {'field1': value1, 'field2': value2}

        Example:
          es = ESEngine()

          # use arxiv_id to specify which doc should be updated
          es.update({'date': '2012-01'}, arxiv_id='2101.01710')
        """

        if not doc:
            logger.warning(f'Cannot update empty document. doc: {doc}')

        # if not doc_id:
        #     # if doc_id is not provided, get doc_id by `search_by_arxiv_id`
        #     assert arxiv_id, 'Neither `doc_id` or `arxiv_id` is provided'
        #     doc_id = self.search_by_arxiv_id(arxiv_id)['_id']

        body = {'doc': doc}
        self.es.update(index='arxiv', doc_type='_doc', id=arxiv_id, body=body)

    def delete_all(self) -> None:
        """ Delete all the documents in index `arxiv`

        Example:
          es = ESEngine()
          es.delete_all()
        """
        self.es.indices.delete(index='arxiv')


if __name__ == '__main__':

    es = ESEngine()
    # es.search('summarization', fields=['title', 'abstract'], size=2)

    es.update({'date': 'updated'}, arxiv_id='2101.01677')

    # res = es.search_by_arxiv_id('H07V1nYBefzuKKfTVRTv')
    # print(res)
    # papers = es.search('summarization', ['abstract'])
    # papers = [Paper(json=p) for p in papers]
    # print(papers)

# es
# es = es_connect()
# es_delete(es)

# es = es_connect()
# keyword = "summarization"
# papers = recommand_randomly(keyword)
# papers = [p.get_json() for p in papers]
# es_index_bulk(es, papers)
# es_search(es)
