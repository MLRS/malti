import argparse
import os
from argparse import ArgumentError
from pathlib import Path
import dataset_processors
from malti2arabi import translit
from text_utils import dediacritise_malti






DATASET_PROCESSORS = {
    "korpus_malti": dataset_processors.KorpusMaltiProcessor,
    "part_of_speech": dataset_processors.InceptionTsvDatasetProcessor,
    "universal_dependencies": dataset_processors.UniversalDependenciesDatasetProcessor,
    "wikiann": dataset_processors.WikiAnnDatasetProcessor,
    "sentiment_analysis": dataset_processors.SentimentAnalysisDatasetProcessor,
}


def transliterate(dataset_processor: dataset_processors.DatasetProcessor,
                  input_path: Path,
                  output_path: Path):
    def preprocess(text):
        return dediacritise_malti(text)
    def process(text):
        text = preprocess(text)
        return translit(text)

    for input_file_path in Path(input_path).rglob("*" + dataset_processor.file_extension):
        if input_file_path.is_file():
            dataset_processor.process(process,
                                      input_file_path=input_file_path,
                                      output_file_path=os.path.join(output_path, input_file_path.name))


def main():
    parser = argparse.ArgumentParser("Transliterates Maltese datasets to Arabic script.")
    parser.add_argument("dataset_processor",
                        choices=DATASET_PROCESSORS.keys(),
                        help="The type of data to transliterate. "
                             "Only the source text is transliterated, any annotations are kept as is.")
    parser.add_argument("input_path",
                        type=str,
                        help="The input directory from where data is read.")
    parser.add_argument("output_path",
                        type=str,
                        help="The output directory where the data is written to. "
                             "If the directory doesn't exist, it will be created. "
                             "If the directory exists, any files which have the same file name from the input, "
                             "will be overwritten.")
    args = parser.parse_args()

    dataset_processor = DATASET_PROCESSORS[args.dataset_processor]()

    input_path = Path(args.input_path)
    if not input_path.is_dir():
        raise ArgumentError(None, "Input path should refer to a directory!")

    output_path = Path(args.output_path)
    os.makedirs(output_path, exist_ok=True)
    if not output_path.is_dir():
        raise ArgumentError(None, "Output path should refer to a directory!")

    transliterate(dataset_processor, input_path, output_path)


if __name__ == "__main__":
    main()
