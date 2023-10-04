import argparse
import logging
import os
import pickle
from pathlib import Path
from typing import Callable, Optional, Union

from sklearn.base import BaseEstimator

import dataset_processors
import token_rankers
from etymology_classification import featurise
from translate import translate_token, get_available_translations
from transliterate import transliterate

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
            model: Optional[BaseEstimator],
            actions: Union[dict[str, Callable[[str], str]], Callable[[str], str]]) -> None:
    def _process(tokens):
        if model:
            tags = model.predict([featurise(tokens)])[0]
            return [actions.get(tag, lambda token: token)(token) for token, tag in zip(tokens, tags)]
        else:
            return [actions(token) for token in tokens]

    assert isinstance(actions, dict) if model else callable(actions)
    dataset_processor.process(_process,
                              input_path,
                              output_path)


def main():
    parser = argparse.ArgumentParser("Processes Maltese dataset tokens")
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
    parser.add_argument("--etymology_model",
                        type=str,
                        help="A model which is used to make predictions on the etymology of tokens in the data. "
                             "This should be a file path which refers to a model that can be pickled "
                             "(this should have a `predict` method which takes lists of pre-tokenised sentences). "
                             "This model is used when any of the processing actions is done exclusively, "
                             "so when multiple actions are specified and/or an action is done on a subset of classes.")
    parser.add_argument("--transliterate", "-x",
                        type=str,
                        nargs="*",
                        help="If specified, this indicates that the tokens should be processed using transliteration. "
                             "Etymology classes can be specified to only transliterate the selected classes "
                             "(this requires that the `etymology_model` should be specified).")
    parser.add_argument("--translate", "-t",
                        type=str,
                        nargs="*",
                        help="If specified, this indicates that the tokens should be processed using translation. "
                             "Etymology classes can be specified to only translation the selected classes "
                             "(this requires that the `etymology_model` should be specified). "
                             "The `translation_system` is always required regardless of whether classes are specified.")
    parser.add_argument("--translation_system",
                        choices=get_available_translations(),
                        nargs="+",
                        help="The translations to use. "
                             "Can specify a single translation system to use for all classes or multiple systems. "
                             "When multiple systems are specified, the number of systems specified "
                             "should be equal to the number of classes specified in `translate`."
                             "Only used when `translate` is specified.")
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
                        help="The models to use for each token ranker. "
                             "The order specified should match that specified for the rankers. "
                             "These are optional & should be left empty for rankers which don't require a model.")
    args = parser.parse_args()

    dataset_processor = DATASET_PROCESSORS[args.dataset_processor]()

    input_path = Path(args.input_path)
    if not input_path.is_dir():
        parser.error("Input path should refer to a directory!")

    output_path = Path(args.output_path)
    os.makedirs(output_path, exist_ok=True)
    if not output_path.is_dir():
        parser.error("Output path should refer to a directory!")

    if args.rankers:
        if args.ranker_models:
            assert len(args.rankers) == len(args.ranker_models)
        else:
            args.ranker_models = ["" for _ in range(len(args.ranker_models))]
        ranker_args = [[model] if model else [] for model in args.ranker_models]
        rankers = [RANKERS[ranker](*args) for ranker, args in zip(args.rankers, ranker_args)]
    else:
        rankers = None

    systems = {
        "transliterate": (args.transliterate, lambda token: transliterate(token, args.token_mappings, rankers)),
    }

    if args.translate is not None:
        if not args.translation_system:
            parser.error("translation_system is required when translating")
        elif len(args.translation_system) == 1:
            systems[f"translate"] = \
                (args.translate, lambda token: translate_token(token, args.translation_system[0]))
        elif len(args.translation_system) > 1:
            if len(args.translation_system) != len(args.translate):
                parser.error("translation_systems should correspond to the classes specified in translate")
            for translate_class, system in zip(args.translate, args.translation_system):
                systems[f"translate {translate_class}"] = \
                    ([translate_class], lambda token: translate_token(token, system))

    exclusive_name = None
    actions = {}
    for name, (classes, action) in systems.items():
        if classes is not None and len(classes) == 0:
            if exclusive_name:
                parser.error(f"Cannot {name} exclusively since you specified to {exclusive_name} exclusively!")
            exclusive_name = name
        else:
            for x in classes or []:
                if x in actions:
                    logging.warning(f"Ignoring {name} action for {x}, because it's already assigned!")
                actions[x] = action
    if exclusive_name:
        assert len(actions) == 0
        actions = systems[exclusive_name][1]

    model = None
    if not exclusive_name:
        if not args.etymology_model:
            parser.error("An etymology model is required when processing with multiple actions")
        with open(args.etymology_model, "rb") as file:
            model = pickle.load(file)
    elif args.etymology_model:
        logging.warning(f"Etymology model will not be used since you chose to {exclusive_name} exclusively")

    process(
        dataset_processor,
        input_path,
        output_path,
        model,
        actions,
    )


if __name__ == "__main__":
    main()
