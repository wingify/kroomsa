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
from pymongo import UpdateOne
from utils.mongo_helper import Mongo
from emojis.add_emojis import Emoji


class PostProcess:
    """
        Processes the submissions in mongo,
        adds additional flags and emojis
    """
    def close(self):
        """Closes the connection to the database"""
        self.connection.close()

    def __init__(self, with_emoji=False):
        self.connection = Mongo(demo_mode=False)
        self.coll = self.connection.coll
        self.add_flags()
        self.custom_question_answer()
        if with_emoji:
            Emoji()
        self.close()

    def add_flags(self):
        """Adds informative flags to the submissions"""
        query = {"$set": {
                            "Status": "Not known",
                            "instant_showable": False,
                            'comment_ind': -1,
                            'emojis': []
                        }
                 }
        self.coll.update_many({}, query, upsert=False, array_filters=None)

    def is_this_ans(self, comment, score_threshold=2):
        """
           Checks if the comment can be used as the
           answer to the submission
        """
        # Returns a flag whether this is the answer to give
        if int(comment['score']) < score_threshold:
            # Not enough upvotes
            return False
        if comment['body'] == '[removed]':
            # comment removed by the moderator
            return False
        if comment['author'] == "" or comment['author'] == " ":
            if comment['body'] != "[deleted]" and comment['body'] != "":
                return True
            # Comment deleted by the user
            else:
                return False
        return True

    def check_status(self, question):
        """
           Determines the status of the submission
        """
        if int(question['score']) >= 2:
            if question['title'] == "":
                return "Empty title"
            if 'removed_by_category' in question.keys():
                if (question['author'] == '[deleted]' and
                        question['removed_by_category'] == "author"):
                    return "Removed by Author"
                if 'selftext' in question.keys():
                    if (question['selftext'] == '[removed]' and
                            question['removed_by_category'] == 'moderator'):
                        return "Removed by the moderator"
                return "Removed by {}".format(question['removed_by_category'])
            else:
                if 'selftext' in question.keys():
                    if (question['selftext'] == '[removed]' or
                            question['selftext'] == '[deleted]'):
                        return "removed"
            return "Exists"
        return "Low score"

    def custom_question_answer(self):
        """
           Determines if a suitable answer exists
           for a submission in the scraped comments
        """
        batch = list()
        # Reads the entire database
        documents = self.coll.find().hint("id_1")
        for document in documents:
            doc_id = document['int_id']
            # checking if the post itself is removed by mod/User
            status = self.check_status(document)
            ans_exists = False
            ans_ind = -1
            if status == "Exists":
                try:
                    comments = list(document['comments'])
                    for i in range(len(comments)):
                        # Checking if this comment can be the answer
                        if self.is_this_ans(comments[i]):
                            # update the informative flags
                            ans_exists = True
                            ans_ind = i
                            break
                except Exception as error:
                    print("Error: {}".format(error))
            # updating the post
            batch.append(
                        UpdateOne(
                                    {
                                        'int_id': doc_id
                                    },
                                    {"$set": {
                                                "Status": status,
                                                "instant_showable": ans_exists,
                                                'comment_ind': ans_ind
                                            }
                                     },
                                    hint="int_id_1",
                                    upsert=False,
                                    array_filters=None
                                )
                        )
            if len(batch) >= 500000:
                print("Updating flags")
                self.coll.bulk_write(batch, ordered=False)
                batch = list()
        if len(batch) != 0:
            print("Updating the final batch")
            self.coll.bulk_write(batch, ordered=False)


if __name__ == "__main__":
    PostProcess(with_emoji=True)  # Set False to ignore emotes
