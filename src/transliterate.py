import argparse
import os
from argparse import ArgumentError
from pathlib import Path
from typing import Optional

import dataset_processors
import token_rankers
from translit import transliterate_sequence

DATASET_PROCESSORS = {
    "mlrs_pos": dataset_processors.ConllDatasetProcessor,
    "universal_dependencies": dataset_processors.UniversalDependenciesDatasetProcessor,
    "mapa": dataset_processors.MapaDatasetProcessor,
    "sentiment_analysis": dataset_processors.SentimentAnalysisDatasetProcessor,
}

RANKERS = {
    "random": token_rankers.RandomRanker,
    "sub_tokens_count": token_rankers.SubTokensCountRanker,
    "word_model_score": token_rankers.WordModelScoreRanker,
    "character_model_score": token_rankers.CharacterModelScoreRanker,
}


def process(dataset_processor: dataset_processors.DatasetProcessor,
            input_path: Path,
            output_path: Path,
            token_mappings: Optional[list[str]],
            token_rankers: Optional[list[token_rankers.TokenRanker]]):
    dataset_processor.process(lambda tokens: transliterate_sequence(tokens, token_mappings, token_rankers),
                              input_path,
                              output_path)


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
    parser.add_argument("--token_mappings",
                        type=str,
                        nargs="+",
                        help="The token mappings to use in addition to the character mappings. "
                             "If unspecified, no token mappings are used.")
    parser.add_argument("--rankers",
                        choices=RANKERS.keys(),
                        nargs="+",
                        help="The token ranker to use whenever there are multiple alternatives to choose from. "
                             "When specified, the non-deterministic character mappings are used, "
                             "otherwise the deterministic character mappings are used if not.")
    parser.add_argument("--ranker_models",
                        type=str,
                        nargs="+",
                        help="The models to use for each token ranker."
                             "The order specified should match that specified for the rankers."
                             "These are optional & should be left empty for rankers which don't require a model.")
    args = parser.parse_args()

    dataset_processor = DATASET_PROCESSORS[args.dataset_processor]()

    input_path = Path(args.input_path)
    if not input_path.is_dir():
        raise ArgumentError(None, "Input path should refer to a directory!")

    output_path = Path(args.output_path)
    os.makedirs(output_path, exist_ok=True)
    if not output_path.is_dir():
        raise ArgumentError(None, "Output path should refer to a directory!")

    if args.rankers:
        if args.ranker_models:
            assert len(args.rankers) == len(args.ranker_models)
        else:
            args.ranker_models = ["" for _ in range(len(args.ranker_models))]
        ranker_args = [[model] if model else [] for model in args.ranker_models]
        rankers = [RANKERS[ranker](*args) for ranker, args in zip(args.rankers, ranker_args)]
    else:
        rankers = None

    process(
        dataset_processor,
        input_path,
        output_path,
        args.token_mappings,
        rankers,
    )


if __name__ == "__main__":
    main()
