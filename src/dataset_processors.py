import abc
import json
from dataclasses import dataclass
from typing import Callable, Iterator, List, IO


class Instance(abc.ABC):
    """
    An instance in a dataset.
    """

    @abc.abstractmethod
    def process_text(self, processor: Callable[[str], str]):
        """
        Processes the input text.
        If the :class:`Instance` contains multiple texts, the `processor` can be invoked multiple times.

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

    def process(self, processor: Callable[[str], str], input_file_path, output_file_path):
        """
        Iterates a given file from the dataset to process it.
        The labels are rewritten as-is in the output file.

        Args:
            processor: A function which takes the text from the data as an argument & returns the processed text.
            input_file_path: The file path to read data from.
            output_file_path: The file path to write the processed data to
            (if it already exists, it will be overwritten).
        """

        with open(input_file_path, "r", encoding="utf-8") as input_file, \
                open(output_file_path, "w", encoding="utf-8") as output_file:
            for instance in self._read(input_file):
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


class KorpusMaltiProcessor(DatasetProcessor):
    """
    Processes the `Korpus Malti <https://huggingface.co/datasets/MLRS/korpus_malti>`_. dataset.
    The file format is `JSON Lines https://jsonlines.org/>`_ where each JSON object is expected to have this form:
        `{"text": ["text0", "text1"]}`
    """

    class Instance(Instance):

        def __init__(self, data):
            self.data = data

        def process_text(self, processor: Callable[[str], str]):
            self.data["text"] = [processor(text) for text in self.data["text"]]

    @property
    def file_extension(self) -> str:
        return ".jsonl"

    def _read(self, file: IO) -> Iterator[Instance]:
        for line in file:
            yield KorpusMaltiProcessor.Instance(json.loads(line))

    def _write(self, file: IO, instance):
        assert isinstance(instance, KorpusMaltiProcessor.Instance)
        json.dump(instance.data, file)
        file.write("\n")


class InceptionTsvDatasetProcessor(DatasetProcessor):
    """
    Processes datasets in `INCEpTION TSV <https://inception-project.github.io/>`_ format.
    The text is assumed to be the 2nd column of the file, with any other column being an annotation.
    """

    @dataclass
    class Annotation:
        text: str
        labels: List[str]

    class Instance(Instance):

        def __init__(self):
            self.annotations = []
            self.comment = ""

        def process_text(self, processor: Callable[[str], str]):
            self.annotations = [InceptionTsvDatasetProcessor.Annotation(processor(annotation.text), annotation.labels)
                                for annotation in self.annotations]

        def is_empty(self) -> bool:
            return len(self.annotations) == 0

    @property
    def file_extension(self) -> str:
        return ".tsv"

    def _read(self, file: IO) -> Iterator[Instance]:
        instance = InceptionTsvDatasetProcessor.Instance()
        for line in file:
            line = line.strip()
            if line.startswith("#"):  # start of instance
                instance.comment = line
                continue
            if len(line) == 0:  # end of instance
                yield instance
                instance = InceptionTsvDatasetProcessor.Instance()
                continue

            instance.annotations.append(self._read_line(line))

        if not instance.is_empty():  # trailing instance with no new line at the end
            yield instance

    @staticmethod
    def _read_line(line: str) -> Annotation:
        labels = line.split("\t")
        text = labels.pop(1)
        return InceptionTsvDatasetProcessor.Annotation(text, labels)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, InceptionTsvDatasetProcessor.Instance)
        file.write(instance.comment)
        file.write("\n")
        for annotation in instance.annotations:
            file.write("\t".join([annotation.labels[0]] + [annotation.text] + annotation.labels[1:]) + "\n")
        file.write("\n")


class UniversalDependenciesDatasetProcessor(InceptionTsvDatasetProcessor):
    """
    Processes the `Universal Dependencies <https://universaldependencies.org/>`_ dataset.
    The file format is `CONLL-U <https://universaldependencies.org/format.html>`_.
    """

    @property
    def file_extension(self) -> str:
        return ".conllu"


class WikiAnnDatasetProcessor(DatasetProcessor):
    """
    Processes the `WikiAnn <https://github.com/afshinrahimi/mmner>`_ dataset.
    The file format contains tags for a token on each line as follows:
        `<language>:<token>\t<tag>`
    """

    @dataclass
    class Annotation:
        text: str
        label: str
        language: str

    class Instance(Instance):

        def __init__(self):
            self.annotations = []
            self.comment = ""

        def process_text(self, processor: Callable[[str], str]):
            self.annotations = [WikiAnnDatasetProcessor.Annotation(processor(annotation.text),
                                                                   annotation.label,
                                                                   annotation.language)
                                for annotation in self.annotations]

        def is_empty(self) -> bool:
            return len(self.annotations) == 0

    def _read(self, file: IO) -> Iterator[Instance]:
        instance = WikiAnnDatasetProcessor.Instance()
        for line in file:
            line = line.strip()
            if line.startswith("#"):  # start of instance
                instance.comment = line
                continue
            if len(line) == 0:  # end of instance
                yield instance
                instance = WikiAnnDatasetProcessor.Instance()
                continue

            instance.annotations.append(self._read_line(line))

        if not instance.is_empty():  # trailing instance with no new line at the end
            yield instance

    @staticmethod
    def _read_line(line: str) -> Annotation:
        line = line.strip()
        text, label = line.split("\t", maxsplit=1)
        text, language = text[:3], text[3:]
        return WikiAnnDatasetProcessor.Annotation(text, label, language)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, WikiAnnDatasetProcessor.Instance)
        for annotation in instance.annotations:
            file.write(f"{annotation.language}:{annotation.text}\t{annotation.label}\n")
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

        def process_text(self, processor: Callable[[str], str]):
            self.text = processor(self.text)

    def _read(self, file: IO) -> Iterator[Instance]:
        for line in file:
            label, text = line.split(",", maxsplit=1)
            yield SentimentAnalysisDatasetProcessor.Instance(text.strip(), label)

    def _write(self, file: IO, instance: Instance):
        assert isinstance(instance, SentimentAnalysisDatasetProcessor.Instance)
        file.write(f"{instance.label},{instance.text}\n")
