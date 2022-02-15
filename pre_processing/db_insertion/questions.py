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
from utils.mongo_helper import Mongo
from config import config


def question_insert(drop_coll=True):
    """Inserts the scraped questions into mongo"""
    # Database connection
    connection = Mongo(demo_mode=False)
    coll = connection.coll
    if drop_coll:
        # Start fresh
        coll.drop()
        last_id = 0
    else:
        # Continue adding to an existing collection
        last_doc = list(coll.find().sort([(
                                            'int_id',
                                            -1
                                           )]).limit(1))
        last_id = last_doc[0]['int_id']
        last_id = last_id + 1

    # scraped questions dir
    scraped_questions_path = os.path.join(
                                        config['scraping']['questions_path'],
                                        "*.json"
                                        )
    scraped_questions = glob.glob(scraped_questions_path)
    for file in scraped_questions:
        questions = json.load(open(file, 'rb'))
        print("Number of posts: {}".format(len(questions)))
        batch = list()
        for i in range(len(questions)):
            questions[i]['int_id'] = last_id
            last_id += 1
            batch.append(questions[i])
            if len(batch) > 2000:
                coll.insert_many(batch)
                batch = list()
        # Inserting the final batch
        if len(batch) != 0:
            coll.insert_many(batch)
    # Creating indexes
    coll.create_index([("int_id", 1)])
    coll.create_index([("id", 1)])
    print("Created database indexes")
    # Closing the connection to db
    connection.close()


if __name__ == '__main__':
    # Inserts the scraped questions after dropping the existing db
    question_insert(True)
