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
import faiss
import tensorflow as tf
from config import config
# Setting visible devices to 0
os.environ['CUDA_VISIBLE_DEVICES'] = "0"


class Index:
    """
        Loads the CPU index into RAM,
        checks for GPU's presence
        If detected, index is loaded in GPU
    """
    def read_index(self):
        """Reads the combined FAISS index"""
        combined_index_path = os.path.join(
                                    config['root_dir'],
                                    config['index']['combined_rel'],
                                    'reddit_combined.faiss'
                                    )
        # Reading index in RAM
        combined_index = faiss.read_index(combined_index_path)
        self.index['CPU'] = combined_index
        # Check to detect a GPU
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if(len(gpus)) != 0:
            # GPU is present
            print("Setting gpu growth")
            tf.config.experimental.set_memory_growth(gpus[0], True)
            # Allocating resources on GPU
            res = faiss.StandardGpuResources()
            # Transfering CPU index to GPU
            combined_index_gpu = faiss.index_cpu_to_gpu(res, 0, combined_index)
            del combined_index
            self.index['GPU'] = combined_index_gpu

    def __init__(self):
        self.index = {'GPU': None, 'CPU': None}
        self.read_index()
