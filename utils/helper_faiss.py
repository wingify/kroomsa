"""
    * Copyright 2022 Wingify Software Pvt. Ltd.
    *
    * Licensed under the Apache License, Version 2.0 (the "License");
    * you may not use this file except in compliance with the License.
    * You may obtain a copy of the License at
    *
    *    http://www.apache.org/licenses/LICENSE-2.0
    *
    * Unless required by applicable law or agreed to in writing, software
    * distributed under the License is distributed on an "AS IS" BASIS,
    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    * See the License for the specific language governing permissions and
    * limitations under the License.
"""
# Importing dependencies
import numpy as np
import tensorflow_hub as hub
import tensorflow as tf
from config import config
from .index_loader import Index

# Reading indexes
indexes = Index().index
if indexes['CPU'] is None and indexes['GPU'] is None:
    raise ValueError("All indexes are None")
# Reading vectorizer
embed = hub.load(config['vec_path'])


def process_question(question, post_type, distance):
    """Fetches the selective attributes from Questions that still exist"""
    if question['Status'] == 'Exists':
        # Result object
        res_obj = {
              "Question": question['title'],
              "Answer": None,
              "dist": distance,
              'emojis': question['emojis'],
              "meta": None,
             }
        # Checking if an answer is available
        if question['instant_showable']:
            comment_ind = int(question['comment_ind'])
            res_obj['Answer'] = list(question['comments'])[comment_ind]['body']
        # Populating Meta info
        meta = {
            'numComments': None,
            'subredditName': None,
            'url': None,
            'mediaUrl': None,
            'selftext': None,
        }

        if 'num_comments' in question.keys():
            meta['numComments'] = question['num_comments']

        if 'subreddit' in question.keys():
            meta['subredditName'] = 'r/' + question['subreddit']

        if 'url' in question.keys():
            if post_type == 'self':
                meta['url'] = question['url']
            elif post_type == 'link':
                meta['mediaUrl'] = question['url']
                meta['url'] = url_gen(question['permalink'])

        if 'selftext' in question.keys():
            if post_type == 'self':
                meta['selftext'] = question['selftext']

        res_obj['meta'] = meta
    else:
        res_obj = None
    return res_obj


def url_gen(permalink):
    """Generates accessible URL for a submission"""
    return 'https://www.reddit.com' + permalink


def map_to_db(mongo_client, distances, indices):
    """
       Maps the indices returned by the search to their
       corresponding entries in mongo and returns selective
       attributes of qualified objects as results
    """
    results = list()
    inds = [int(i) for i in list(indices)]
    distances = [float(i) for i in list(distances)]
    questions = list(mongo_client.coll.find({
                                'int_id': {'$in': inds}
                                }).sort([('int_id', 1)]))
    sorted_indices = list(np.argsort(inds))
    for i in range(len(distances)):
        dist = distances[i]
        question = questions[sorted_indices.index(i)]
        if question['is_self']:
            post_type = 'self'
        else:
            post_type = 'link'
        res_obj = process_question(question, post_type, dist)
        if res_obj is not None:
            results.append(res_obj)
    return results


def similar_questions(
                      mongo_client,
                      question,
                      use_gpu=False):
    """
       Vectorises the query and searches the
       index and db for similar entries
    """
    # vectorising question using cpu
    with tf.device('/cpu:0'):
        vector = embed([question]).numpy()
    if use_gpu:
        if indexes['GPU'] is None:
            raise ValueError("Index not loaded")
        distances, indices = indexes['GPU'].search(
                                vector,
                                (config['output']
                                       ['num_documents'])
                                )
    else:
        if indexes['CPU'] is None:
            raise ValueError("Index not loaded")
        distances, indices = indexes['CPU'].search(
                                vector,
                                (config['output']
                                       ['num_documents'])
                                )
    # Mapping indices to entries in mongo
    result = map_to_db(
                    mongo_client,
                    distances[0],
                    indices[0]
                )
    return result
