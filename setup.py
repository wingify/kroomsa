"""
    Runs the setup to create directory structure
"""
# Importing dependencies
import os
from os.path import exists
from config import config


def check_dir_structure():
    """
        Sets up the directory structure
    """
    vec_path = config['vec_path']
    mongo_dump_path = os.path.join(
                            config['root_dir'],
                            'mongo_dump'
                        )
    emote_model_path = os.path.join(
                            config['root_dir'],
                            'post_processing',
                            'emojis',
                            'model'
                        )
    index_path = os.path.join(
                        config['root_dir'],
                        config['index']['combined_rel']
                    )
    scraped_questions_path = (config['scraping']
                                    ['questions_path'])
    questions_partition_path = (config['scraping']
                                      ['partition_id_root'])
    scraped_comments_path = (config['scraping']
                                   ['comments_path'])
    if exists(vec_path) is False:
        print("Creating vectorizer path")
        os.mkdir(vec_path)
    if exists(mongo_dump_path) is False:
        print("Creating mongo_dump path")
        os.mkdir(mongo_dump_path)
    if exists(emote_model_path) is False:
        print("Creating emote_model path")
        os.mkdir(emote_model_path)
    if exists(index_path) is False:
        print("Creating index path")
        os.mkdir(index_path)
    if exists(scraped_questions_path) is False:
        print("Creating questions path for scraping")
        os.mkdir(scraped_questions_path)
    if exists(scraped_comments_path) is False:
        print("Creating comments path for scraping")
        os.mkdir(scraped_comments_path)
    if exists(questions_partition_path) is False:
        print("Creating path for partitioned ids of submissions")
        os.mkdir(questions_partition_path)


if __name__ == '__main__':
    try:
        check_dir_structure()
    except Exception as e:
        raise e
