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
from pymongo import MongoClient
from config import config


class Mongo:
    """
        Connects to the running mongo instance,
        Initialises the connection to db and collection
        specified by the config
    """
    def close(self):
        """closes the connection to db"""
        self.client.close()

    def __init__(
                 self,
                 demo_mode,
                 ip_addr=config['mongo']['ip'],
                 port=config['mongo']['port'],
                 db_name=config['mongo']['db'],
                 coll=config['mongo']['coll'],
                 ):
        if demo_mode is True:
            # dockerized demo
            ip_addr = 'mongo_db'
        self.client = MongoClient(ip_addr, port)
        self.db_name = self.client[db_name]
        self.coll = self.db_name[coll]
