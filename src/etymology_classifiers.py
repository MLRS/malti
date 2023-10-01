from collections import defaultdict, Counter

import numpy as np
from sklearn.base import BaseEstimator
from sklearn_crfsuite import CRF


class MaximumLikelihoodEstimateClassifier(BaseEstimator):
    def __init__(self, feature=0):
        """
        A Maximum Likelihood Estimate classifier which predicts the most likely label for a seen feature.
        If a given feature is seen with multiple labels, the most frequently seen label is chosen.
        If the feature is never seen, the most likely label overall is chosen.

        :param feature: The feature to discriminate on when memorising predictions.
        """
        self.token_memory = defaultdict(Counter)
        self.label_memory = Counter()
        self.feature = feature

    def fit(self, X, y):
        self.token_memory = defaultdict(Counter)
        for X_sequence, y_sequence in zip(X, y):
            for text, label in zip(X_sequence, y_sequence):
                self.token_memory[text[self.feature]].update([label])
            self.label_memory.update(y_sequence)

        return self

    def predict(self, X):
        return [[self.predict_token(token) for token in sequence] for sequence in X]

    def predict_token(self, token: str) -> str:
        counter = self.get_token_counts(token)
        return (counter if len(counter) > 0 else self.label_memory).most_common(1)[0][0]

    def get_token_counts(self, token: str) -> Counter:
        return self.token_memory[token[self.feature]]

    def is_certain(self, token: str) -> bool:
        """
        :param token: The token to check.
        :return: Whether the given token is only seen with 1 target label.
        """
        return len(self.get_token_counts(token)) == 1


class MleCrfClassifier(BaseEstimator):
    def __init__(self, mle: MaximumLikelihoodEstimateClassifier, crf: CRF):
        """
        An ensemble model which combines a :class:`MaximumLikelihoodEstimateClassifier` & a :class:`CRF`.
        The prediction from `mle` is used if it's 100% confident (it saw the token with a single label during training),
        otherwise the `crf` predictions are used as a fall-back.

        :param mle: The :class:`MaximumLikelihoodEstimateClassifier` model.
        :param crf: The :class:`CRF` model.
        """
        self.mle = mle
        self.crf = crf

    def fit(self, X, y):
        self.mle.fit(X, y)
        self.crf.fit(X, y)

    def predict(self, X):
        return np.array([
            [
                mle_prediction if self.mle.is_certain(word) else crf_prediction
                for word, mle_prediction, crf_prediction in zip(*sequence)
            ] for sequence in zip(X, self.mle.predict(X), self.crf.predict(X))
        ], dtype=object)


class TranslationDistanceClassifier(BaseEstimator):
    """
    A classifier based on heuristics between the token & the distance with its translations.
    This implementation is specific to Maltese as it is based on Arabic, Italian, & English distances.
    """

    def __init__(self, feature=0):
        self.memory = defaultdict(Counter)
        self.feature = feature

    def fit(self, X, y):
        return self

    def predict(self, X):
        def _predict(word):
            arabic_distance = word["arabic_distance"]
            italian_distance = word["italian_distance"]
            english_distance = word["english_distance"]
            if italian_distance == 0 and english_distance == 0:
                if word["contains_digit"] or word["contains_punctuation"]:
                    return "Symbol"
                else:
                    return "Name"
            elif italian_distance == 0 or english_distance == 0:
                return "Code-Switching"

            minimum_distance = min(arabic_distance, italian_distance, english_distance)
            if arabic_distance == minimum_distance:
                return "Arabic"
            else:
                return "Non-Arabic"

        return [[_predict(word) for word in sequence] for sequence in X]
