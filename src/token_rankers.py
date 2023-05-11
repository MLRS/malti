import abc

import kenlm
import numpy as np
from transformers import AutoTokenizer


class TokenRanker(abc.ABC):
    best_score_selector = max
    """
    The function to use when choosing the best score.
    This can be overridden by inheritors & is mostly applicable with the default implementation of :py:meth:`~TokenRanker.filter_best`.
    """

    def filter_best(self, alternatives: list[str]) -> list[str]:
        """
        Args:
            alternatives: All the alternative tokens to consider.

        Returns:
            The filtered list of alternatives which have the best score.
            If multiple alternatives are given,
            this means that all the alternatives are considered equally good by the :class:`TokenRanker`.
        """
        scores = self.score(alternatives)
        return np.asarray(alternatives)[np.asarray(scores) == self.best_score_selector(scores)]

    @abc.abstractmethod
    def score(self, alternatives: list[str]) -> list[float]:
        """
        Args:
            alternatives: All the alternative tokens to consider.

        Returns:
            A score for each token of the given ``alternatives``.
        """
        pass


class RandomRanker(TokenRanker):
    """
    Ranks tokens by sorting them alphabetically.
    """

    def filter_best(self, alternatives: list[str]) -> list[str]:
        return [sorted(alternatives)[0]]

    def score(self, alternatives: list[str]) -> list[float]:
        pass


class SubTokensCountRanker(TokenRanker):
    """
    Ranks tokens by the number of sub-tokens given by the underlying tokenizer.
    """

    best_score_selector = min

    def __init__(self, name: str):
        """
        Args:
            name: The name or path to the tokenizer to use from the ``transformers`` library.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(name)

    def score(self, alternatives: list[str]) -> list[float]:
        return self.tokenizer(alternatives, add_special_tokens=False, return_length=True)["length"]


class WordModelScoreRanker(TokenRanker):
    """
    Ranks tokens by the word n-gram language model score.
    """

    def __init__(self, name: str):
        """
        Args:
            name: The path to the model to use through the ``kenlm`` library.
        """
        self.model = kenlm.Model(name)

    def score(self, alternatives: list[str]) -> list[float]:
        return [self.model.score(token) for token in alternatives]


class CharacterModelScoreRanker(TokenRanker):
    """
    Ranks tokens by the character n-gram language model score.
    """

    def __init__(self, name: str):
        """
        Args:
            name: The path to the model to use through the ``kenlm`` library.
        """
        self.model = kenlm.Model(name)

    def score(self, alternatives: list[str]) -> list[float]:
        return [self.model.score(' '.join(token)) for token in alternatives]
