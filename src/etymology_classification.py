# adapted from https://github.com/HaifaCLG/Denglisch/blob/74c68f1f47fdd92dcfe77ce67dd8d3637aeadac0/code/classifier.py

import argparse
import csv
import itertools
import logging
import os
import string
import warnings
from typing import Any

import pandas as pd
from Levenshtein import distance
from nltk import ngrams
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import KFold
from tqdm import tqdm

import token_rankers
from etymology_classifiers import *
from token_mappings import get_token_mappings
from translate import translate_token
from transliterate import transliterate

COLLECTIONS = {}


def get_collection(path: str) -> list[str]:
    if path not in COLLECTIONS:
        with open(path, "r", encoding="utf-8") as file:
            collection = []
            for line in file:
                collection.append(line.strip())
            COLLECTIONS[path] = collection
    return COLLECTIONS[path]


CLOSED_CLASS_MAPPINGS_PATHS = ["token_mappings/small_closed_class.map", "token_mappings/additional_closed_class.map"]
CLOSED_CLASS_TOKENS = []
RANKER_MODELS_BASE_PATH = "../models/"
RANKERS = []


def get_closed_class_tokens() -> list[str]:
    global CLOSED_CLASS_TOKENS
    if not CLOSED_CLASS_TOKENS:
        for file_path in CLOSED_CLASS_MAPPINGS_PATHS:
            CLOSED_CLASS_TOKENS += list(get_token_mappings(file_path).keys())
    return CLOSED_CLASS_TOKENS


def _transliterate(token):
    global RANKERS
    if not RANKERS:
        RANKERS = [
            token_rankers.WordModelScoreRanker(
                os.path.join(RANKER_MODELS_BASE_PATH, "aggregated_country/lm/word/tn-maghreb.arpa")),
            token_rankers.CharacterModelScoreRanker(
                os.path.join(RANKER_MODELS_BASE_PATH, "aggregated_country/lm/char/tn-maghreb.arpa")),
        ]

    return transliterate(token, CLOSED_CLASS_MAPPINGS_PATHS, RANKERS)


def featurise(sequence: list[str]) -> list[dict[str, Any]]:
    """
    :param sequence: The sequence of tokens.
    :return: The tokens converted to features to be used by the model.
    """
    x = []
    for index in range(len(sequence)):
        token = sequence[index]
        token_lower = token.lower()

        common_maltese_ngrams = get_collection("etymology_data/common_ngrams.txt")
        list_of_ngrams = ["".join(ngram) for ngram in itertools.chain.from_iterable(
            ngrams(token_lower, length) for length in set(len(ngram) for ngram in common_maltese_ngrams)
        )]

        arabic_translation = translate_token(token, "mt-ar")
        italian_translation = translate_token(token, "mt-it")
        english_translation = translate_token(token, "mt-en")
        transliteration = _transliterate(token)
        features = {
            "token": token,
            "token_lower": token_lower,
            "all_upper": token.isupper(),
            "contains_upper": token.istitle(),
            "contains_digit": any(char.isdigit() for char in token) and token.isnumeric() is False,
            "all_digit": token.isnumeric(),
            "contains_maltese_characters": any(char in "ċġħż" for char in token_lower),
            "contains_punctuation": any(char in string.punctuation for char in token),
            "all_punctuation": all(char in string.punctuation for char in token),

            "is_closed_class_token": token_lower in get_closed_class_tokens(),
            "contains_common_ngrams": any(ngram in common_maltese_ngrams for ngram in list_of_ngrams),

            "arabic_translation": arabic_translation,
            "italian_translation": italian_translation,
            "english_translation": english_translation,
            "transliteration": transliteration,

            "arabic_distance": distance(transliteration, arabic_translation),
            "italian_distance": distance(token_lower, italian_translation.lower()),
            "english_distance": distance(token_lower, english_translation.lower()),
        }

        for ngram in common_maltese_ngrams:
            features[ngram] = ngram in list_of_ngrams

        if index == 0:
            features["BOS"] = True
        if index == len(sequence) - 1:
            features["EOS"] = True

        x.append(features)

    return x


def k_fold_cross_validation(X, y, classifier, k=10, shuffle=False, random_seed=None):
    """
    :param X: The input features.
    :param y: The target labels.
    :param classifier: An object which has `fit(X, y)` & `predict(y)` methods
                       to train the classifier & classify instances, respectively.
    :param k: The number of splits to perform for cross-validation.
    :param shuffle: Whether to shuffle the samples before splitting.
    :param random_seed: The random seed to use when shuffling.
    :return: A tuple of features, labels, & predictions, each being a list of batches &
             sorted by rounds of cross-validation (i.e. the first element of each list is an array containing
             the features/targets/predictions from the first round).
    """

    X = np.array(list(X), dtype=object)
    y = np.array(list(y), dtype=object)

    feature_list, label_list, prediction_list = [], [], []

    kf = KFold(n_splits=k, shuffle=shuffle, random_state=random_seed)
    for train_ids, test_ids in tqdm(kf.split(X), desc=f"Cross-Validation", total=k):
        X_train = X[train_ids]
        y_train = y[train_ids]
        X_test = X[test_ids]
        y_test = y[test_ids]

        seen_words = set(features["token_lower"] for instance in X_train for features in instance)

        classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_test)

        feature_list.append([
            [
                {**features, "seen": features["token_lower"] in seen_words}
                for features in instance
            ]
            for instance in X_test
        ])
        label_list.append(y_test.copy())
        prediction_list.append(y_pred.copy())

    return feature_list, label_list, prediction_list


def print_metrics_seen_unseen_splits(label_list, feature_folds, label_folds, prediction_folds):
    # Temporarily disable all warnings to suppress warnings about ill-defined metrics.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        print("\nALL")
        print_metrics(label_list, feature_folds, label_folds, prediction_folds)

        seen_labels = []
        unseen_labels = []
        seen_predictions = []
        unseen_predictions = []
        for X_test, y_test, y_pred in zip(feature_folds, label_folds, prediction_folds):
            y_test_seen = []
            y_test_unseen = []
            y_pred_seen = []
            y_pred_unseen = []
            for features_fold, labels_fold, predictions_fold in zip(X_test, y_test.tolist(), y_pred):
                y_test_fold_seen = []
                y_test_fold_unseen = []
                y_pred_fold_seen = []
                y_pred_fold_unseen = []
                for features, target, prediction in zip(features_fold, labels_fold, predictions_fold):
                    if features["seen"]:
                        y_test_fold_seen.append(target)
                        y_pred_fold_seen.append(prediction)
                    else:
                        y_test_fold_unseen.append(target)
                        y_pred_fold_unseen.append(prediction)
                y_test_seen.append(y_test_fold_seen)
                y_test_unseen.append(y_test_fold_unseen)
                y_pred_seen.append(y_pred_fold_seen)
                y_pred_unseen.append(y_pred_fold_unseen)
                assert len(y_test_seen[-1]) == len(y_test_seen[-1])
                assert len(y_test_unseen[-1]) == len(y_test_unseen[-1])
            seen_labels.append(y_test_seen)
            unseen_labels.append(y_test_unseen)
            seen_predictions.append(y_pred_seen)
            unseen_predictions.append(y_pred_unseen)
            assert len(seen_labels[-1]) == len(seen_predictions[-1])
            assert len(unseen_labels[-1]) == len(unseen_predictions[-1])

        print("\nSEEN")
        print_metrics(label_list, feature_folds, seen_labels, seen_predictions)
        print("\nUNSEEN")
        print_metrics(label_list, feature_folds, unseen_labels, unseen_predictions)


def print_metrics(label_list, features, labels, predictions):
    """
    Prints metrics, averaging over folds.

    :param label_list: The set of labels.
    :param features: The input features, batched by folds & sentence.
    :param labels: The target labels, batched by folds & sentence.
    :param predictions: The predicted labels, batched by folds & sentence.
    """
    scores = defaultdict(lambda: defaultdict(list))

    y_tests = []
    y_preds = []
    for X_test, y_test, y_pred in zip(features, labels, predictions):
        y_test_fold = []
        for sent_sublist in y_test:
            for tag_val in sent_sublist:
                y_test_fold.append(tag_val)
        y_pred_fold = []
        for sent_sublist in y_pred:
            for tag_val in sent_sublist:
                y_pred_fold.append(tag_val)
        y_tests += y_test_fold
        y_preds += y_pred_fold

        for key, value in classification_report(y_test_fold, y_pred_fold, output_dict=True).items():
            if not isinstance(value, dict):
                value = {"": value}
            for sub_key, sub_value in value.items():
                scores[key][sub_key].append(sub_value)

    print("\t" + "\t".join(next(iter(scores.values())).keys()))
    for key, value in scores.items():
        print(f"{key}\t", end="")
        for sub_key, sub_value in value.items():
            print(f"{np.mean(sub_value) :{'.0' if sub_key == 'support' else '.2%'}}\t", end="")
        print()

    cm = confusion_matrix(y_tests, y_preds, labels=label_list)
    cm = ((cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]) * 100)  # normalise for class imbalance
    print("\t".join(label_list))
    print(cm)


def read_data(file_name, label_column):
    data = pd.read_csv(file_name, delimiter="\t", quoting=csv.QUOTE_NONE)
    tokens, tags = [], []
    ids = data["id"].drop_duplicates()
    for id in ids:
        sentence = data[data["id"] == id]
        tokens.append(list(sentence["token"]))
        tags.append(list(sentence[label_column]))

    features = [featurise(sentence) for sentence in tqdm(tokens, desc="Generating features")]
    return tokens, features, tags


def evaluate(model, data, num_rounds, random_seed=None):
    tokens, features, tags = data

    tagset = set()
    for sentence_tags in tags:
        tagset.update(sentence_tags)
    tagset = list(tagset)

    features_folds, labels_fold, predictions_fold = \
        k_fold_cross_validation(features, tags, model, k=num_rounds, shuffle=True, random_seed=random_seed)
    print_metrics_seen_unseen_splits(tagset, features_folds, labels_fold, predictions_fold)


MODELS = {
    "mle+crf": lambda: MleCrfClassifier(MODELS["mle"](), MODELS["crf"]()),
    "crf": lambda: CRF(algorithm='lbfgs', c1=0.1, c2=0.1, max_iterations=100, all_possible_transitions=True),
    "mle": lambda: MaximumLikelihoodEstimateClassifier(feature="token_lower"),
    "translation": lambda: TranslationDistanceClassifier(),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path",
                        type=str,
                        help="The file path to a TSV file containing the data annotations.")
    parser.add_argument("--model",
                        default=list(MODELS.keys())[0],
                        choices=MODELS.keys(),
                        help="The model type to train.")
    parser.add_argument("--cross_validation_folds",
                        type=int,
                        default=10,
                        help="The number of folds for cross-validation.")
    parser.add_argument("--label_column",
                        type=str,
                        default="category_merged",
                        help="The column to use as a label for classification, "
                             "corresponding to a heading in the `data_path` file.")
    parser.add_argument("--random_seed",
                        type=int,
                        default=None,
                        help="The random seed to use when splitting the data into folds.")
    args = parser.parse_args()

    data = read_data(args.data_path, args.label_column)

    model = MODELS[args.model]()
    evaluate(model, data, args.cross_validation_folds, args.random_seed)


if __name__ == "__main__":
    main()
