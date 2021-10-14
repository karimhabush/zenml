#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os
from typing import Type

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from zenml.materializers.base_materializer import BaseMaterializer
from zenml.utils import yaml_utils

DATA_FILENAME = "data.parquet"
SHAPE_FILENAME = "shape.json"
DATA_VAR = "data_var"


class NumpyMaterializer(BaseMaterializer):
    """Materializer to read data to and from pandas."""

    ASSOCIATED_TYPES = [np.ndarray]

    def handle_input(self, data_type: Type) -> np.ndarray:
        """Reads numpy array from parquet file."""
        shape_dict = yaml_utils.read_json(
            os.path.join(self.artifact.uri, SHAPE_FILENAME)
        )
        shape_tuple = tuple(shape_dict.values())
        data = pq.read_table(os.path.join(self.artifact.uri, DATA_FILENAME))
        vals = getattr(data.to_pandas(), DATA_VAR).values
        return np.reshape(vals, shape_tuple)

    def handle_return(self, arr: np.ndarray):
        """Writes a np.ndarray to the artifact store as a parquet file.

        Args:
            arr: The numpy array to write.
        """
        yaml_utils.write_json(
            os.path.join(self.artifact.uri, SHAPE_FILENAME),
            {i: x for i, x in enumerate(arr.shape)},
        )
        pa_table = pa.table({DATA_VAR: arr.flatten()})
        pq.write_table(pa_table, os.path.join(self.artifact.uri, DATA_FILENAME))
