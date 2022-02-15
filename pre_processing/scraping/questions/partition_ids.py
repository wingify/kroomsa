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
from config import config


def read(file):
    """Reads the file and extracts the ids"""
    submission_ids = list()
    data = json.load(open(file, "r", encoding='utf-8'))
    for submission in data:
        submission_ids.append(submission['id'])
    return submission_ids


def save(partition_ind, data):
    """Dumps the parititions as json files"""
    save_path = os.path.join(
                            config['scraping']['partition_id_root'],
                            "ids_{}.json".format(str(partition_ind)))
    json.dump(data, open(save_path, "w", encoding='utf-8'))


def partition(
              num_partitions=len(config['scraping']['bot_codes'])
              ):
    """Partitions the submissions for parallel execution of comment scrapers"""
    scraped_questions_files = os.path.join(
                                        config['scraping']['questions_path'],
                                        '*_*.json'
                                        )
    files = glob.glob(scraped_questions_files)

    # Collecting the list of all available ids
    submission_ids = list()
    for file in files:
        print("Processing file: {}".format(file))
        ids = read(file)
        submission_ids.extend(ids)

    # Partitioning submission_ids
    total_ids = len(submission_ids)
    ids_per_partition = total_ids // num_partitions
    partitioned_ids = list()
    for i in range(num_partitions):
        start_ind = i * ids_per_partition
        end_ind = start_ind + ids_per_partition
        if i == num_partitions - 1:
            # Last partition
            partitioned_ids.append(submission_ids[start_ind:])
        else:
            partitioned_ids.append(submission_ids[start_ind: end_ind])
    # saving the partitioned_ids as json files
    for data, partition_ind in zip(
                                   partitioned_ids,
                                   range(len(partitioned_ids))
                                   ):
        save(partition_ind, data)


if __name__ == '__main__':
    partition(len(config['scraping']['bot_codes']))
