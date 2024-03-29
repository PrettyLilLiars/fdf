# coding=utf-8
# Copyright 2024 The TensorFlow Datasets Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Flickr Diverse Faces"""

import os
import urllib

import numpy as np

from tensorflow_datasets.core.utils.lazy_imports_utils import tensorflow as tf
import tensorflow_datasets.public_api as tfds

_URL = "https://api.loke.aws.unit.no/dlr-gui-backend-resources-content/v2/contents/links/"
RESOURCES = {
  "metadata": tfds.download.Resource(url=urllib.parse.urljoin(_URL, "b704049a-d465-4a07-9cb3-ca270ffab80292e4d5ac-6172-4d37-bf63-4438f61f8aa0e1f6483d-5d45-40b5-b356-10b71fc00e89")),
  "cc-by-nc-sa-2": tfds.download.Resource(url=urllib.parse.urljoin(_URL, "33bb6132-a30e-4169-a09e-48b94cd5e09010fd8f59-1db9-4192-96f0-83d18adf50b4ee3ab25c-b8f8-4c40-a8ba-eaa64d830412")),
  "cc-by-2": tfds.download.Resource(url=urllib.parse.urljoin(_URL, "cb545564-120f-4f35-8b68-63e59e4fd273b1c36452-21e7-4976-85dd-a86c0738ebc256264f20-f969-4a82-ae1c-f6345d8e8d1f")),
  "cc-by-sa-2": tfds.download.Resource(url=urllib.parse.urljoin(_URL, "4e5c27bd-f5fd-4dd3-bf2b-4434a8952df0ff4d11f8-e993-4517-9378-b35d89e7882ecae76ce7-88a0-417b-b5d8-e030863e97f6")),
  "cc-by-nc-2": tfds.download.Resource(url=urllib.parse.urljoin(_URL, "da46d666-4378-4e75-9182-e683ebe08f2e9203750f-7ed8-42f7-8bce-90a7dfddd3764401df36-a3c3-4d39-ae8e-0cb4397e5c74")),
}

FDF_IMAGE_SHAPE = (256, 256, 3)


class Builder(tfds.core.GeneratorBasedBuilder):
  """FDF Builder class."""

  VERSION = tfds.core.Version("0.1.0")

  def _info(self):
    return self.dataset_info_from_configs(
        features=tfds.features.FeaturesDict({
          "image": tfds.features.Image(shape=FDF_IMAGE_SHAPE),
          "landmarks": {
            'nose': tfds.features.Tensor(shape=(2,)),
            'r_eye': tfds.features.Tensor(shape=(2,)),
            'l_eye': tfds.features.Tensor(shape=(2,)),
            'r_ear': tfds.features.Tensor(shape=(2,)),
            'l_ear': tfds.features.Tensor(shape=(2,)),
            'r_shoulder': tfds.features.Tensor(shape=(2,)),
            'l_shoulder': tfds.features.Tensor(shape=(2,)),
          },
          "bbox": tfds.features.BBoxFeature(),
        }),
        supervised_keys=None,
        homepage="https://github.com/hukkelas/FDF/tree/master",
    )

  def _split_generators(self, dl_manager):
    output_files = dl_manager.download_and_extract(RESOURCES)

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                "output_files": output_files,
                "split": "train",
            },
        ),
        tfds.core.SplitGenerator(
          name=tfds.Split.VALIDATION,
          gen_kwargs={
            "output_files": output_files,
            "split": "val",
          }
        )
    ]

  def _generate_examples(self, output_files, split):
    image_list = self.get_image_paths(output_files=output_files, split=split)
    bounds = self.load_bounds(
      bounds_path=os.path.join(output_files['metadata'], split, "bounding_box.npy")
    )
    landmarks = self.load_landmarks(
      landmarks_path=os.path.join(output_files['metadata'], split, "landmarks_box.npy")
    )
    for image, bound in zip(image_list, bounds):
      key = "%s/%s" % (os.path.basename(image), bound)
      yield key, {
          "image": image,
          "landmarks": landmarks,
          "bbox": bound
      }

  def get_image_paths(self, output_files: dict, split):
    paths:list[str] = []
    for license in output_files.keys():
      dir = os.path.join(output_files[license], split, 'images')
      if license == 'metadata' or not os.path.exists(dir):
        pass
      else:
        paths += [os.path.join(dir, x) for x in os.listdir(dir)]
    paths = sorted(paths, key=lambda x: int(os.path.basename(x).removesuffix('.png')))
    return paths

  def load_bounds(self, bounds_path) -> np.ndarray:
    bounds = np.load(bounds_path)
    bounds = np.divide(bounds, 256.)
    return bounds

  def load_landmarks(self, landmarks_path) -> dict:
    landmarks = np.load(landmarks_path)
    landmarks = np.divide(landmarks, 256.)
    landmarks = {
      'nose': landmarks[0],
      'r_eye': landmarks[1],
      'l_eye': landmarks[2],
      'r_ear': landmarks[3],
      'l_ear': landmarks[4],
      'r_shoulder': landmarks[5],
      'l_shoulder': landmarks[6],
    }
    return landmarks
