from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ES_HOST, \
    AWS_ES_REGION
# from arxiv_api import recommand_randomly

sort = [
    "_score",
    {
        "date": {
            "order": "asc"
        }
    }
]


def es_connect():
    service = 'es'
    awsauth = AWS4Auth(
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ES_REGION, service)

    es = Elasticsearch(
        hosts=[{'host': AWS_ES_HOST, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    print(es.info(), end='\r\n\r\n')
    return es


def es_index(es, doc):

    es.index(index="arxiv", doc_type="_doc", body=doc)

    print(es.get(index="arxiv", doc_type="_doc"))


def es_index_bulk(es, docs):
    body = []
    for doc in docs:
        body.append({'index': {'_index': 'arxiv'}})
        body.append(doc)

    res = es.bulk(doc_type='doc', body=body)
    print(res)


def es_search(es, size=5):
    # https://www.cnblogs.com/ExMan/p/11323984.html
    # body = {
    #     "query": {
    #         "match_all": {
    #         }
    #     }
    # }

    body = {
        'query': {
            'multi_match': {
                'query': 'summarization',
                'fields': ['title', 'abstract']
            }
        },
        "sort": sort
    }
    res = es.search(index='arxiv', body=body, size=size)
    res = res['hits']['hits']
    for r in res:
        print(r, end='\r\n\r\n')
    # print(res)


def es_delete(es):
    es.indices.delete(index='arxiv')
# es_delete(es)


es = es_connect()
# keyword = "summarization"
# papers = recommand_randomly(keyword)
# papers = [p.get_json() for p in papers]
# es_index_bulk(es, papers)
# es_search(es)
