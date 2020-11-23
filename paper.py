import re


def clear_text(text):
    text = text.strip()
    text = re.sub(r'[\r|\n]', '', text)
    return text


class Paper:
    def __init__(self, entry):

        self.link = clear_text(entry.find(
            'id').string) if entry.find('id') else '-'
        self.title = clear_text(entry.find(
            'title').string) if entry.find('title') else '-'
        self.abstract = clear_text(entry.find(
            'summary').string[:300]) if entry.find('summary') else '-'

        self.comment = clear_text(entry.find(
            'arxiv:comment').string) if entry.find('arxiv:comment') else '-'
        self.date = clear_text(entry.find(
            'published').string[:7]) if entry.find('published') else '-'

        self.authors = []
        for author in entry.find_all('author'):
            self.authors.append(clear_text(author.find('name').string))

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
                        "text": self.abstract,
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
