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
from flask import Flask, request, jsonify
from utils.helper_faiss import similar_questions
from utils.mongo_helper import Mongo
from config import config
# Connecting to the database
connection = Mongo(config['demo_mode'])
# Init flask app
app = Flask("kroomsa")


@app.route('/health')
def health_check():
    """Checks the status of the service"""
    status = dict()
    # Checking mongo
    try:
        count = connection.coll.estimated_document_count()
        if count >= 0:
            status["Mongo"] = "Working"
        else:
            raise ValueError(
                    """Number of documents retrieved are not as
                    specified in the configuration"""
                )
    except ValueError as error:
        status['Mongo'] = str(error)
    sample_question = "How are rainbows formed?"
    # Checking CPU Index service
    try:
        docs = similar_questions(
                    connection,
                    sample_question,
                    False
                )
        if len(docs) == int(config['output']['num_documents']):
            status['Service(CPU)'] = 'Working'
        else:
            status['Service(CPU)'] = "Unknown error"
            raise ValueError("Incorrect document number")
    except ValueError as error:
        status['Service(CPU)'] = str(error)
    # Checking GPU Index service
    try:
        docs = similar_questions(
                    connection,
                    sample_question,
                    True
                )
        if len(docs) == int(config['output']['num_documents']):
            status['Service(GPU)'] = 'Working'
        else:
            status['Service(GPU)'] = "Unknown error"
            raise ValueError("Incorrect document number")
    except ValueError as error:
        status['Service(GPU)'] = str(error)
    return jsonify(status)


@app.route("/questionCPU")
def get_posts_cpu():
    """Returns n similar questions to the query using CPU index"""
    try:
        question = request.args.get("q").lower()
        result = similar_questions(
                        connection,
                        question,
                        False
                    )
    except ValueError as error:
        result = str(error)
    return jsonify({
        "result": result
    })


@app.route("/questionGPU")
def get_posts_gpu():
    """Returns n similar questions to the query using GPU index"""
    try:
        question = request.args.get("q").lower()
        result = similar_questions(
                        connection,
                        question,
                        True
                    )
    except ValueError as error:
        result = str(error)
    return jsonify({
        "result": result
    })


if __name__ == "__main__":
    app.run(port=80, host="0.0.0.0")
