# coding=utf-8
# Copyright 2020 The TensorFlow Datasets Authors and the HuggingFace NLP Authors.
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

# Lint as: python3
"""Heuristic Analysis for NLI Systems"""

from __future__ import absolute_import, division, print_function

import nlp


_CITATION = """\
@article{DBLP:journals/corr/abs-1902-01007,
  author    = {R. Thomas McCoy and
               Ellie Pavlick and
               Tal Linzen},
  title     = {Right for the Wrong Reasons: Diagnosing Syntactic Heuristics in Natural
               Language Inference},
  journal   = {CoRR},
  volume    = {abs/1902.01007},
  year      = {2019},
  url       = {http://arxiv.org/abs/1902.01007},
  archivePrefix = {arXiv},
  eprint    = {1902.01007},
  timestamp = {Tue, 21 May 2019 18:03:36 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1902-01007.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
"""

_DESCRIPTION = """\
The HANS dataset is an NLI evaluation set that tests specific hypotheses about invalid heuristics that NLI models are likely to learn.
"""


class HansConfig(nlp.BuilderConfig):
    """BuilderConfig for HANS."""

    def __init__(self, **kwargs):
        """BuilderConfig for HANS.

            Args:
        .
              **kwargs: keyword arguments forwarded to super.
        """
        super(HansConfig, self).__init__(
            version=nlp.Version("1.0.0", "New split API (https://tensorflow.org/datasets/splits)"), **kwargs
        )


class Hans(nlp.GeneratorBasedBuilder):
    """Hans: Heuristic Analysis for NLI Systems."""

    BUILDER_CONFIGS = [
        HansConfig(
            name="plain_text",
            description="Plain text",
        ),
    ]

    def _info(self):
        return nlp.DatasetInfo(
            description=_DESCRIPTION,
            features=nlp.Features(
                {
                    "premise": nlp.Value("string"),
                    "hypothesis": nlp.Value("string"),
                    "label": nlp.features.ClassLabel(names=["entailment", "non-entailment"]),
                }
            ),
            # No default supervised_keys (as we have to pass both premise
            # and hypothesis as input).
            supervised_keys=None,
            homepage="https://github.com/tommccoy1/hans",
            citation=_CITATION,
        )

    def _vocab_text_gen(self, filepath):
        for _, ex in self._generate_examples(filepath):
            yield " ".join([ex["premise"], ex["hypothesis"]])

    def _split_generators(self, dl_manager):

        train_path = dl_manager.download_and_extract(
            "https://raw.githubusercontent.com/tommccoy1/hans/master/heuristics_train_set.txt"
        )
        valid_path = dl_manager.download_and_extract(
            "https://raw.githubusercontent.com/tommccoy1/hans/master/heuristics_evaluation_set.txt"
        )

        return [
            nlp.SplitGenerator(name=nlp.Split.TRAIN, gen_kwargs={"filepath": train_path}),
            nlp.SplitGenerator(name=nlp.Split.VALIDATION, gen_kwargs={"filepath": valid_path}),
        ]

    def _generate_examples(self, filepath):
        """Generate hans examples.

        Args:
          filepath: a string

        Yields:
          dictionaries containing "premise", "hypothesis" and "label" strings
        """
        for idx, line in enumerate(open(filepath, "rb")):
            if idx == 0:
                continue  # skip header
            line = line.strip().decode("utf-8")
            split_line = line.split("\t")
            # Examples not marked with a three out of five consensus are marked with
            # "-" and should not be used in standard evaluations.
            if split_line[0] == "-":
                continue
            # Works for both splits even though dev has some extra human labels.
            yield idx, {"premise": split_line[5], "hypothesis": split_line[6], "label": split_line[0]}
