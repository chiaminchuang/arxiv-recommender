import re


def clear_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text


class Paper:
    def __init__(self, entry=None, json=None):

        assert (entry or json) and (not entry or not json)
        self.arxiv_id = ''
        self.link = ''
        self.title = ''
        self.abstract = ''
        self.comment = ''
        self.date = ''
        self.authors = []

        if entry:
            self._from_html(entry)
        if json:
            self._from_json(json)

    def _from_html(self, entry):

        # _id = http://arxiv.org/abs/2012.03930v1
        _id = entry.find('id').string

        # 2012.03930
        self.arxiv_id = re.search(
            r'([\d|.]+)[v|\d]+', _id, re.IGNORECASE).group(1)
        self.link = _id

        self.title = clear_text(entry.find(
            'title').string) if entry.find('title') else '-'
        self.abstract = clear_text(entry.find(
            'summary').string) if entry.find('summary') else '-'

        self.comment = clear_text(entry.find(
            'arxiv:comment').string) if entry.find('arxiv:comment') else '-'
        self.category = [e.attrs['term'] for e in entry.find_all('category')]
        self.date = clear_text(entry.find(
            'published').string[:7]) if entry.find('published') else '-'

        self.authors = []
        for author in entry.find_all('author'):
            self.authors.append(clear_text(author.find('name').string))

    def _from_json(self, json):
        self.link = json['link']
        self.title = json['title']
        self.abstract = json['abstract']
        self.comment = json['comment']
        self.date = json['date']
        self.authors = json['authors']

    def __repr__(self):
        return self.get_json()

    def __str__(self):
        return f'''Paper(
            arxiv_id={self.arxiv_id},
            link={self.link},
            title={self.title},
            summary={self.summary},
            abstract={self.abstract},
            authors={self.authors},
            comment={self.comment},
            category={','.join(self.category)},
            date={self.date})'''

    def get_json(self):
        return {
            'arxiv_id': self.arxiv_id,
            'link': self.link,
            'title': self.title,
            'abstract': self.abstract,
            'author': self.authors,
            'comment': self.comment,
            'category': self.category,
            'date': self.date
        }

    def get_flex_contents(self):
        return {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": self.title,
                        "size": "md",
                        "weight": "bold"
                    }
                ]
            },
            "hero": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": ', '.join(self.authors),
                        "size": "xxs",
                        "style": "italic",
                        "offsetStart": "xxl"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": self.abstract[:300] + ' ...',
                        "wrap": True,
                        "size": "sm"
                    }
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": self.comment,
                                "size": "xs",
                                "style": "italic",
                                "wrap": True,
                                "offsetStart": "md"
                            },
                            {
                                "type": "text",
                                "text": self.date,
                                "size": "xs",
                                "style": "italic",
                                "offsetStart": "md"
                            },
                            {
                                "type": "spacer"
                            }
                        ]
                    },
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "Study",
                            "uri": self.link
                        },
                        "height": "sm",
                        "style": "primary"
                    }
                ]
            },
            "styles": {
                "footer": {
                    "separator": False
                }
            }
        }
