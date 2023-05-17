import abc
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator, IO

from tqdm import tqdm


class Instance(abc.ABC):
    """
    An instance in a dataset.
    """

    @abc.abstractmethod
    def process_text(self, processor: Callable[[list[str]], list[str]]):
        """
        Processes the input text.

        Args:
            processor: A function which takes the instance text as an argument & returns its processed form.
        """
        pass


class DatasetProcessor(abc.ABC):
    """
    Iterates over datasets to process their text leaving any labels/metadata intact.
    """

    @property
    def file_extension(self) -> str:
        """
        Returns:
            The file extension used for the dataset, if any.
        """
        return ""

    def process(self, processor: Callable[[list[str]], list[str]], input_path, output_path):
        """
        Iterates a directory for files from the dataset to process it,
        based on the :py:meth:`~DatasetProcessor.file_extension`.
        The labels are rewritten as-is in the output file.

        Args:
            processor: A function which takes the tokens from the data as an argument & returns the processed tokens.
            input_path: The directory path to read data from.
            output_path: The directory path to write the processed data to
            (if a file already exists, it will be overwritten).
        """

        for input_file_path in Path(input_path).rglob("*" + self.file_extension):
            if input_file_path.is_file():
                output_file_path = os.path.join(output_path, input_file_path.name)
                with open(input_file_path, "r", encoding="utf-8") as input_file, \
                        open(output_file_path, "w", encoding="utf-8") as output_file:
                    for instance in tqdm(self._read(input_file), desc=f"Processing {input_file.name}"):
                        instance.process_text(processor)
                        self._write(output_file, instance)

    @abc.abstractmethod
    def _read(self, file: IO) -> Iterator[Instance]:
        """
        Args:
            file: The file to read data from.

        Returns:
            The :class:`Instance`s in that file.
        """

        pass

    @abc.abstractmethod
    def _write(self, file: IO, instance):
        """
        Args:
            file: The file to write data to.
            instance: The :class:`Instance` to write.
        """

        pass


class ConllDatasetProcessor(DatasetProcessor):
    """
    Processes datasets in CoNLL format.
    The text is assumed to be the 2nd column of the file, with any other column being an annotation.
    """

    @dataclass
    class Annotation:
        text: str
        labels: list[str]

    class Instance(Instance):

        def __init__(self):
            self.annotations = []
            self.comment = ""

        def process_text(self, processor: Callable[[list[str]], list[str]]):
            for i, token in enumerate(processor([annotation.text for annotation in self.annotations])):
                self.annotations[i].text = token

        def is_empty(self) -> bool:
            return len(self.annotations) == 0

    @property
    def file_extension(self) -> str:
        return ".tsv"

    def _read(self, file: IO) -> Iterator[Instance]:
        instance = ConllDatasetProcessor.Instance()
        for line in file:
            line = line.strip()
            if line.startswith("#"):  # start of instance
                instance.comment = line
                continue
            if len(line) == 0:  # end of instance
                yield instance
                instance = ConllDatasetProcessor.Instance()
                continue

            instance.annotations.append(self._read_line(line))

        if not instance.is_empty():  # trailing instance with no new line at the end
            yield instance

    @staticmethod
    def _read_line(line: str) -> Annotation:
        labels = line.split("\t")
        text = labels.pop(1)
        return ConllDatasetProcessor.Annotation(text, labels)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, ConllDatasetProcessor.Instance)
        file.write(instance.comment)
        file.write("\n")
        for annotation in instance.annotations:
            file.write("\t".join([annotation.labels[0]] + [annotation.text] + annotation.labels[1:]) + "\n")
        file.write("\n")


class UniversalDependenciesDatasetProcessor(ConllDatasetProcessor):
    """
    Processes the `Universal Dependencies <https://universaldependencies.org/>`_ dataset.
    The file format is `CONLL-U <https://universaldependencies.org/format.html>`_.
    """

    @property
    def file_extension(self) -> str:
        return ".conllu"


class MapaDatasetProcessor(DatasetProcessor):
    """
    Processes the MAPA dataset.
    The file format is in JSONlines, where each line contains an instance as a JSON object.
    Each JSON object contains a list of strings under the `"tokens"` key, corresponding to the tokens to be processed.
    """

    class Instance(Instance):

        def __init__(self, data):
            self.data = data

        def process_text(self, processor: Callable[[list[str]], list[str]]):
            self.data["tokens"] = processor([token for token in self.data["tokens"]])

    @property
    def file_extension(self) -> str:
        return ".json"

    def _read(self, file: IO) -> Iterator[Instance]:
        for line in file:
            if line.strip() == 0:
                break

            data = json.loads(line)
            yield MapaDatasetProcessor.Instance(data)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, MapaDatasetProcessor.Instance)
        json.dump(instance.data, file, ensure_ascii=False)
        file.write("\n")


class SentimentAnalysisDatasetProcessor(DatasetProcessor):
    """
    Processes the `Multilingual Sentiment Analysis <https://github.com/jerbarnes/typology_of_crosslingual/tree/master/data/sentiment>`_ dataset.
    The file format is CSV of 2 columns denoting the label & the text.
    """

    @dataclass
    class Annotation:
        text: str
        label: str

    class Instance(Instance):

        def __init__(self, text, label):
            self.text = text
            self.label = label

        def process_text(self, processor: Callable[[list[str]], list[str]]):
            tokens = self.text.split(" ")
            self.text = " ".join(processor(tokens))

    @property
    def file_extension(self) -> str:
        return ".csv"

    def _read(self, file: IO) -> Iterator[Instance]:
        for line in file:
            label, text = line.split(",", maxsplit=1)
            text = text.strip("\" ").strip()
            yield SentimentAnalysisDatasetProcessor.Instance(text, label)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, SentimentAnalysisDatasetProcessor.Instance)
        file.write(f"{instance.label},{instance.text}\n")
