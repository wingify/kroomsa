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
import glob
import json
from pymongo import UpdateOne
from config import config
from utils.mongo_helper import Mongo


def comment_insert():
    """
       Reads the scraped comments,
       cleans them, and inserts them into mongo
    """
    # Connecting to the db
    connection = Mongo(demo_mode=False)
    # Scraped comments dir
    scraped_comments_path = os.path.join(
                                        config['scraping']['comments_path'],
                                        '*.json'
                                        )
    scraped_comments = glob.glob(scraped_comments_path)
    scraped_comments.sort()
    batch = list()
    for file in scraped_comments:
        print("Currently processing: {}".format(file))
        data = json.load(open(file, "r", encoding='utf-8'))
        count = 0
        for key, comment in data.items():
            batch.append(UpdateOne(
                                    {
                                     'id': str(key)
                                     },
                                    {'$set': {
                                              'comments': comment
                                              }
                                     },
                                    hint=("id_1"),
                                    upsert=False,
                                    array_filters=None
                                   ))
            count += 1
        if len(batch) >= 100000:
            print("Adding Comments to db")
            connection.coll.bulk_write(batch, ordered=False)
            batch = list()
    # Writing the last batch
    if len(batch) != 0:
        print("Adding the final batch")
        connection.coll.bulk_write(batch, ordered=False)
        batch = list()
    # Closing the connection to db
    connection.close()


if __name__ == "__main__":
    comment_insert()
