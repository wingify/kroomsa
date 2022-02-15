# Kroomsa

<img src="https://raw.githubusercontent.com/wingify/kroomsa/master/images/kroomsa.svg" alt="Kroomsa" width="50" height="50"/>

A search engine for the curious. It is a search algorithm designed to engage users by exposing them to relevant yet
interesting content during their session.

## Description

The search algorithm implemented in your website greatly influences visitor engagement. A decent implementation can significantly reduce dependency on standard search engines like Google for every query thus,
increasing engagement. Traditional methods look at terms or phrases in your query to find relevant content based on syntactic matching. Kroomsa uses semantic matching to find content relevant to your query.
There is a [blog post](https://engineering.wingify.com/posts/kroomsa-a-search-engine-for-the-curious/) expanding upon Kroomsa's motivation and its technical aspects.

## Getting Started

### Prerequisites

* Python 3.6.5
* Run the project directory setup: ```python3 ./setup.py``` in the root directory.
* Tensorflow's Universal Sentence Encoder 4
  * The model is available at this [link](https://tfhub.dev/google/universal-sentence-encoder/4).
   Download the model and extract the zip file in the `/vectorizer` directory.
* MongoDB is used as the database to collate Reddit's submissions. MongoDB can be installed following this [link](https://docs.mongodb.com/manual/administration/install-community/).
* To fetch comments of the reddit submissions, PRAW is used. To scrape credentials are needed that authorize the script for the same. This is done by creating an app associated with a reddit account by following this [link](https://www.reddit.com/wiki/api). For reference you can follow this [tuorial](https://new.pythonforengineers.com/blog/build-a-reddit-bot-part-1/) written by [Shantnu Tiwari](https://new.pythonforengineers.com/author/shantnu/).
  * Register multiple instances and retrieve their credentials, then add them to the `/config` under `bot_codes` parameter in the following format: ```"client_id client_secret user_agent"``` as list elements separated by `,`.
* Docker-compose (For dockerized deployment only): Install the latest version following this [link](https://docs.docker.com/compose/install/).

### Installing

* Create a python environment and install the required packages for preprocessing using: ```python3 -m pip install -r ./preprocess_requirements.txt```
* Collating a dataset of Reddit submissions
  * Scraping posts
    * Pushshift's API is being used to fetch Reddit submissions. In the root directory, run the following command: ```python3 ./pre_processing/scraping/questions/scrape_questions.py```. It launches a script that scrapes the subreddits sequentially till their inception and stores the submissions as JSON objects in `/pre_processing/scraping/questions/scraped_questions`. It then partitions the scraped submissions into as many equal parts as there are registered instances of bots.
  * Scraping comments
    * After populating the configuration with `bot_codes`, we can begin scraping the comments using the partitioned submission files created while scraping submissions. Using the following command: ```python3 ./pre_processing/scraping/comments/scrape_comments.py``` multiple processes are spawned that fetch comment streams simultaneously.
  * Insertion
    * To insert the submissions and associated comments, use the following commands: ```python3 ./pre_processing/db_insertion/insertion.py```. It inserts the posts and associated comments in mongo.
    * To clean the comments and tag the posts that aren't public due to any reason, Run ```python3 ./post_processing/post_processing.py```. Apart from cleaning, it also adds emojis to each submission object (This behavior is configurable).
* Creating a FAISS Index
  * To create a FAISS index, run the following command: ```python3 ./index/build_index.py```. By default, it creates an exhaustive ```IDMap, Flat``` index but is configurable through the ```/config```.
* Database dump (For dockerized deployment)
  * For dockerized deployment, a database dump is required in `/mongo_dump`. Use the following command at the root dir to create a database dump. ```mongodump --db database_name(default: red) --collection collection_name(default: questions) -o ./mongo_dump```.


### Execution

* Local deployment (Using Gunicorn)
  * Create a python environment and install the required packages using the following command: ```python3 -m pip install -r ./inference_requirements.txt```
  * A local instance of Kroomsa can be deployed using the following command:
  ```gunicorn -c ./gunicorn_config.py server:app```
* Dockerized demo
  * Set the `demo_mode` to `True` in `/config`.
  * Build images: ```docker-compose build```
  * Deploy: ```docker-compose up```

## Authors

* [Aakash chawla](https://twitter.com/Aakashc97)
* [Divyanshu Kalra](https://github.com/kalradivyanshu)

## License

This project is licensed under the [Apache License Version 2.0](https://github.com/wingify/kroomsa/blob/master/LICENSE)
