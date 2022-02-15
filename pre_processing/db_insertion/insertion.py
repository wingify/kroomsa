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
from comments import comment_insert
from questions import question_insert


# Parameters
DROP_PREV_DATA = True

if __name__ == '__main__':
    # Inserting submissions in mongo
    question_insert(DROP_PREV_DATA)
    # Inserting corresponding comments
    comment_insert()
