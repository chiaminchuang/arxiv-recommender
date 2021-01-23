import argparse

from src.aws_api import ESEngine
from src.arxiv_api import ArxivSearch

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--query', type=str, default='',
        help='Search query for arxiv paper. Use `,` as separator for multiple query')
    parser.add_argument('--n', type=int, default=10,
                        help='The number of returned results')

    args = parser.parse_args()

    arxiv = ArxivSearch()
    papers = arxiv.search(args.query, args.n)

    es = ESEngine()
    es.index_bulk(papers)

    # es.search('summarization', fields=['title', 'abstract'], size=2)

    # es.update({'date': '2012-07'}, arxiv_id='2101.05795')

    # es.delete_all()

    # es.search(
    #     'adversarial',
    #     fields=['title', 'abstract'],
    #     size=2)
