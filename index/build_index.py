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
import os
import faiss
import numpy as np
import tensorflow_hub as hub
from config import config
from utils.mongo_helper import Mongo

# Loading vectorizer
embed = hub.load(config['vec_path'])
# Connecting to mongo
connection = Mongo(demo_mode=False)
# Reading subreddits from config
subreddits = config['subreddit']


def is_compatible(subreddit, index_type, status):
    """
       Checks if the submission exists and belongs
       to the required type of subreddit
    """
    if status == 'Exists':
        if index_type == 'AV':
            keys = list(subreddits[index_type].keys())
            for key in keys:
                if subreddit in subreddits[index_type][key]:
                    return True
            return False
        elif index_type == 'TEXT':
            if subreddit in subreddits[index_type]:
                return True
            return False
        elif index_type == 'COMBINED':
            if subreddit in subreddits['TEXT']:
                return True
            keys = list(subreddits['AV'].keys())
            for key in keys:
                if subreddit in subreddits['AV'][key]:
                    return True
            return False
    return False


def gen_index(index_type='COMBINED', name='reddit'):
    """
        Generates the FAISS index from the entries
        in mongo that are based on the type specified.
        TYPE: {
                TEXT = text only subreddit entries
                AV = Audio Visual subreddit entries
                COMBINED = TEXT + AV
               }
    """
    # Reading entire database
    questions = connection.coll.find()
    # Enforcing unique questions in the index
    unique_questions = set()
    batch = list()
    ids = list()
    # Initialising FAISS index
    index = faiss.index_factory(
                                config['index']['dim'],
                                config['index']['type']
                                )
    count = 0
    for question in questions:
        # Checking if object is compatible with the type
        if is_compatible(
                         question['subreddit'],
                         index_type,
                         question['Status']
                         ):
            try:
                title = question['title'].lower()
            except Exception as error:
                print(error)
                continue

            if title not in unique_questions:
                batch.append(title)
                ids.append(question['int_id'])
                unique_questions.add(title)
                count += 1

            if len(batch) > 50000:
                print("Adding to index")
                embeddings = embed(batch).numpy()
                index.add_with_ids(np.array(embeddings), np.array(ids))
                batch = []
                ids = []

    if len(batch) != 0:
        print("Adding the final batch")
        embeddings = embed(batch).numpy()
        index.add_with_ids(embeddings, np.array(ids))

    # Saving the index to disk
    save_path = os.path.join(
                            config['root_dir'],
                            config['index']['combined_rel'],
                            "{}_{}.faiss".format(
                                                 name,
                                                 index_type.lower()
                                                 )
                            )
    faiss.write_index(index, save_path)
    print("FINAL COUNT IS: ", count)


if __name__ == '__main__':
    gen_index('COMBINED')
    connection.close()
