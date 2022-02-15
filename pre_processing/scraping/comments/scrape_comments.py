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
import sys
import json
from time import sleep
from multiprocessing import Pool
import praw
from config import config


def serialize(comments):
    """Serializes the PRAW object to keep the parameters needed"""
    proc_comments = list()
    for comment in comments:
        try:
            proc_comment = dict()
            proc_comment['body'] = comment.body
            proc_comment['score'] = comment.score
            proc_comment['author'] = str(comment.author)
            proc_comment['subreddit'] = str(comment.subreddit.display_name)
            proc_comments.append(proc_comment)
        except Exception as error:
            print(
                "Exception while reading comment attributes: {}".format(error)
            )
            continue
    return proc_comments


def get_comments(reddit, sub_id):
    """Fetches top n comments for the given submission id"""
    try:
        submission = reddit.submission(id=sub_id)
        submission.comment_sort = 'top'
        comments = list(submission.comments[:config['num_comments']])
        comments = serialize(comments)
        return comments

    except Exception as error:
        print(error, sys.exc_info())
        return []


def save(name, ind, data):
    """Dumps the scraped comments as json objects"""
    path = os.path.join(
                        config['scraping']['comments_path'],
                        "{}_{}.json".format(name, str(ind))
                        )
    # Dumping comments as json objects
    json.dump(
                data,
                open(path, "w", encoding='utf-8')
                )


def scrape(reddit, partition_ids, name):
    """Runs the scraper on submission ids"""
    comments = dict()
    ind = 0
    for i in range(len(partition_ids)):
        partition_id = partition_ids[i]
        comments[partition_id] = get_comments(reddit, partition_id)
        sleep(0.5)  # adhering to api limits
        if i % 1000 == 0 and i != 0:
            print("Saving ids till {}".format(i))
            save(name, ind, comments)
            ind += 1
            comments = dict()
    if len(comments) != 0:
        # Writing the last batch
        save(name, ind, comments)


def get_ids(code_id):
    """Reads the partitioned submission ids"""
    file_path = os.path.join(
                             config['scraping']['partition_id_root'],
                             "ids_{}.json".format(code_id)
                             )
    name = file_path.split("/")[-1].split(".")[0]
    submission_ids = json.load(open(file_path, "r", encoding='utf-8'))
    return submission_ids, name


def scrape_comments(code_id):
    """
       Scraper that fetches top n comments
       for submission ids in a parition
    """
    # Reading bot code from config
    bot_code = config['scraping']['bot_codes'][code_id]
    client_id, client_secret, user_agent = bot_code.split(" ")
    # Initialising PRAW
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent
                         )
    reddit.config.store_json_result = True
    # Reading parition
    partition_ids, name = get_ids(code_id)
    scrape(reddit, partition_ids, name)


if __name__ == '__main__':
    # Reading number of partitions
    PARTITIONS_NUM = len(config['scraping']['bot_codes'])
    # Parallel execution of comment scrapers
    with Pool(PARTITIONS_NUM) as p:
        p.map(
              scrape_comments,
              range(PARTITIONS_NUM)
              )
