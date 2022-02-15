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
import time
import json
from datetime import datetime
import requests
from partition_ids import partition
from config import config


def process(json_data):
    """Extracts the submissions and updates the previous epoch"""
    data = list()
    if 'data' in json_data:
        objects = json_data['data']
        if len(objects) != 0:
            for obj in objects:
                data.append(obj)
                previous_epoch = obj['created_utc'] - 1
            return data, previous_epoch
    return None, None


def save(data, subreddit_name, index):
    """Saves the extracted submissions as json objects"""
    save_path = os.path.join(
                    config['scraping']['questions_path'],
                    "{}_dump_{}.json".format(
                                        subreddit_name,
                                        str(index)
                                    )
                    )

    # dumping scraped questions as a json obj
    json.dump(
                data,
                open(save_path, "w", encoding='utf-8')
                )


def scrape(api_string, subreddit_name, previous_epoch):
    """
       Scrapes the posts of a subreddit
       from a timestamp till its inception
    """
    data = list()
    ind = 0
    count = 0
    while True:
        # Adding previous_epoch to api string
        new_url = api_string + str(previous_epoch)
        try:
            # Setting user agent as a scraper
            user_agent = subreddit_name + "scraper"
            json_data = requests.get(
                                new_url,
                                headers={
                                        'User-Agent': user_agent
                                        },
                                timeout=120,
                                ).json()
            time.sleep(1)  # adhering to api limits
            objects, previous_epoch = process(json_data)
            if objects is None or previous_epoch is None:
                # We have reached the inception
                break
            data.extend(objects)
            if len(data) > 1000:
                count += len(data)
                # Save as JSON
                save(data, subreddit_name, ind)
                ind += 1
                data = list()
                if ((count >= config['scraping']['submission_num']) and
                   (config['scraping']['submission_num'] != -1)):
                    break
        except Exception as error:
            print(error, sys.exc_info())
            previous_epoch -= 5


def get_submissions(subreddit_name, previous_epoch=None):
    """
       Runs the scraper on a subreddit fetching submissions
       from previous_epoch to its inception
    """
    print("Scraping {}".format(subreddit_name))
    # Generating the pushshift api URL
    url = ("https://api.pushshift.io/reddit/search/submission/?subreddit="
           "{}".format(subreddit_name)
           )
    url += "&limit=1000&sort=desc&before="
    # Last epoch to scrape from
    if previous_epoch is None:
        previous_epoch = int(datetime.utcnow().timestamp())
    # Calling the scraper
    scrape(url, subreddit_name, previous_epoch)
    return 0


if __name__ == '__main__':
    # Getting all the subreddits
    img = config['subreddit']['AV']['IMAGE']
    video = config['subreddit']['AV']['VIDEO']
    text = config['subreddit']['TEXT']
    subreddits = img + video + text
    res = list(map(
                    get_submissions,
                    subreddits
                   )
               )
    # Partitioning the ids
    try:
        print("Partioning ids for efficient comment scraping")
        partition(len(config['scraping']['bot_codes']))
    except Exception as e:
        print("Error occoured: ", e)
