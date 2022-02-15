"""
        The central config for all the parameters in the project
"""
# Importing dependencies
import os


root_dir = os.path.dirname(os.path.abspath(__file__))
config = {
        'root_dir': root_dir,  # Root dir of the project
        'num_comments': 5,  # Max number of comments to fetch
        'vec_path': os.path.join(root_dir, 'vectorizer'),
        'emojis': {
                'num': 3,  # Number of emotes per submission
                'dataset': os.path.join(
                                        root_dir,
                                        'post_processing',
                                        'emojis',
                                        'data',
                                        'emojis.csv'
                                        ),
                'model': os.path.join(
                                        root_dir,
                                        'post_processing',
                                        'emojis',
                                        'model',
                                        'emojiEmbeddings.pt'
                                        ),
                },
        'index': {
                'dim': 512,  # Vector dimensions
                'type': "IDMap,Flat",
                'combined_rel': os.path.join(
                                                'index',
                                                'combined_index'
                                                ),
                },
        'mongo': {
                'ip': 'localhost',
                'port': 27017,
                'db': 'red',
                'coll': 'questions',
                },
        'scraping': {
                'questions_path': os.path.join(
                                                root_dir,
                                                'pre_processing',
                                                'scraping',
                                                'questions',
                                                'scraped_questions'
                                                ),
                'comments_path': os.path.join(
                                                root_dir,
                                                'pre_processing',
                                                'scraping',
                                                'comments',
                                                'scraped_comments'
                                                ),
                'partition_id_root': os.path.join(
                                                root_dir,
                                                'pre_processing',
                                                'scraping',
                                                'questions',
                                                'partitioned_ids'
                                                ),
                'submission_num': -1,  # Keep as -1 to scrape till inception
                'bot_codes': [
                                ]
                },
        'subreddit': {
                        'AV': {
                                'VIDEO': ['lectures', 'Documentaries'],
                                'IMAGE': []
                                },
                        'TEXT': [
                                'NoStupidQuestions',
                                'askscience',
                                'AskHistorians',
                                'explainlikeimfive'
                                ]
                        },
        'output': {
                'num_documents': 20  # Number of submissions in output
        },
        'demo_mode': False  # Set True for dockerized deployment
        }
