# Arxiv Recommender - Linebot

An arxiv paper recommendation system built with Amazon `Lambda` and `Elasticsearch` through `Linebot`.

## Table of Contents

- [Technology](#technology)
- [Features](#features)
- [Demonstration](#demonstration)
- [Setup](#setup)
- [Reference](#reference)

## Technology

### Arxiv API

arXiv is an open-access service created for 1M+ scholarly articles in the fields of physics, mathematics, computer science, etc., and is maintained by Cornell University. <p>
I downloaded the arXiv papers through official arXiv API (arxiv_api.py) and stored them into Elasticsearch hosted on AWS. I restricted the category in `['cs.AI', 'cs.LG', 'cs.CL', 'cs.CV', 'cs.IR'] `because of my personal interests.

| code         | category                                |
| ------------ | --------------------------------------- |
| cs</span>.AI | Artifical Intelligent                   |
| cs</span>.LG | Machine Learning                        |
| cs</span>.CL | Computation and Language                |
| cs</span>.CV | Computer Vision and Pattern Recognition |
| cs</span>.IR | Information Theory                      |

### Linebot

I used Linebot as user interface for the convience. You can check the interesting papers anytime and anywhere. Linebot API was deployed using AWS Lambda, a serverless compute service.

### Elasticsearch

```json
{
  "arxiv_id": "2010.08892",
  "link": "http://arxiv.org/abs/2010.08892v1",
  "title": "Mixed-Lingual Pre-training for Cross-lingual Summarization",
  "abstract": "Cross-lingual Summarization (CLS) aims at producing a summary in the target language for an article in the source language ...",
  "author": [
    "Ruochen Xu",
    "Chenguang Zhu",
    "Yu Shi",
    "Michael Zeng",
    "Xuedong Huang"
  ],
  "comment": "Accepted at Asia-Pacific Chapter of the Association for Computational Linguistics (AACL) 2020",
  "category": ["cs.LG"],
  "date": "2020-10"
}
```

## Features

## Setup

```
set AWS_ACCESS_KEY_ID=YOUR_AWS_KEY
set AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY

sls deploy
```

## Demonstration

Simply type the keyword you're interested in. Use **comma** as separator for multiple keywords. \
<img src="https://i.imgur.com/L3EveHS.gif" width="250" height="400" /> &emsp;&emsp;&emsp;&emsp;
<img src="https://i.imgur.com/5bsMmL7.gif" width="250" height="400" />

## Reference

- [arxiv api](#https://arxiv.org/help/api/user-manual)
