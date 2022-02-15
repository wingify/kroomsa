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
from os.path import exists
import numpy as np
import pandas as pd
from pymongo import UpdateOne
from sentence_transformers import util
from sentence_transformers import SentenceTransformer
from config import config
from utils.mongo_helper import Mongo


class Emoji:
    """
       Identifies n emotes that fit well with the submission
       and updates the submission
    """
    def __init__(self):
        self.connection = Mongo(demo_mode=False)
        self.load_dataset()
        self.load_embedder()
        self.update_emotes()
        self.connection.close()

    def load_dataset(self):
        """
           Loads the dataset that maps
           emojis to their english interpretation
        """
        self.dataset = pd.read_csv(config['emojis']['dataset'])

    def load_embedder(self):
        """Loads the distilbert model for embedding"""
        model_name = 'distilbert-base-nli-stsb-mean-tokens'
        self.embedder = SentenceTransformer(model_name)
        # check if emote embeddings exist
        if exists(config['emojis']['model']) is False:
            # Create emote embeddings
            emote_embeddings = self.embedder.encode(
                                list(self.dataset['description']),
                                convert_to_tensor=True
                                )
            util.torch.save(emote_embeddings, config['emojis']['model'])
        self.embeddings = util.torch.load(config['emojis']['model'])

    def get_emotes(self, title, num_emojis=config['emojis']['num']):
        """Determines n most similar emotes to a submission"""
        emotes_return = list()
        emotes = list(self.dataset['emote'])
        question_embedding = self.embedder.encode(title, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(
                                          question_embedding,
                                          self.embeddings
                                          )[0]
        cos_scores = cos_scores.cpu()
        top_results = np.argpartition(
                                      -cos_scores,
                                      range(num_emojis)
                                      )[0:num_emojis]
        for index in top_results:
            emotes_return.append({
                                'emoji': emotes[index],
                                'score': float(cos_scores[index]).__round__(2)
                                })
        return emotes_return

    def update_emotes(self):
        """Updates the qualified submissions with most similar emojis"""
        batch = list()
        documents = list(self.connection.coll.find({
                                                    'emojis': [],
                                                    'Status': 'Exists'
                                                    })
                         )
        print("found: {} documents without emojis".format(len(documents)))
        for document in documents:
            doc_id = document['int_id']
            # Try to fetch the emojis
            try:
                emojis = self.get_emotes(document['title'])
            except Exception as error:
                print("Error: {}".format(error))
            # updating the post
            batch.append(UpdateOne(
                                   {
                                    'int_id': doc_id
                                    },
                                   {"$set": {
                                             "emojis": emojis
                                             }
                                    },
                                   hint="int_id_1",
                                   upsert=False,
                                   array_filters=None
                                   ))
            if len(batch) >= 100000:
                print("Updating Emojis")
                self.connection.coll.bulk_write(batch)
                batch = list()

        if len(batch) != 0:
            print("Updating the final batch")
            self.connection.coll.bulk_write(batch)


if __name__ == '__main__':
    Emoji()
