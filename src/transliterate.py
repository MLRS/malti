import logging
import re

from sklearn.feature_extraction.text import strip_accents_unicode

from malti2arabi_fst import translit_word
from token_rankers import RandomRanker, TokenRanker


def strip_plus(x):
    if x == "+":
        return x
    else:
        return x.rstrip("+")


def dediacritise_non_malti_accents(text: str, diacritics_to_keep: str = "ċġħżĊĠĦŻ") -> str:
    """
    Removes diacritics from the text.
    This preserves any special symbols which aren't diacritised characters.
    Args:
        text: The text to dediacritise.
        diacritics_to_keep: Optional diacritics to keep in the text.
    Returns:
        The dediacritised text.
    """

    normalised_text = strip_accents_unicode(text)
    if diacritics_to_keep:
        for character in re.finditer(rf"[{diacritics_to_keep}]", text):
            normalised_text = normalised_text[:character.start()] \
                              + character.group() \
                              + normalised_text[character.end():]
    return normalised_text


def transliterate(token: str,
                  token_mappings: list[str] = None,
                  token_rankers: list[TokenRanker] = None,
                  return_token_merge: bool = False):
    """
    Transliterates a Maltese token to a corresponding Arabic token.

    :param token: The token to transliterate.
    :param token_mappings: The token mappings to use in addition to the character mappings.
    :param token_rankers: The rankers to use when for non-deterministic character mappings.
                          The order specifies which ranker to apply first & which rankers to use for tie-breaks.
                          When tie-breaks cannot be resolved after going through all rankers,
                          these are resolved using :class:`RandomRanker`.
                          When this is unspecified, a deterministic mapping is used.
    :param return_token_merge: Indicates whether to return an additional value indicating a token merge.
    :return: The transliterated token.
             When the transliterated token maps to multiple tokens in the target,
             these are returned as a single string joined with a `" "`.
             If `return_token_merge` is `True`, another value is also returned, indicating whether the token should be
             seperated from the next token with a space (`False`) or merged with the next token (`True`).
    """

    if token_rankers is None:
        token_rankers = []
    if token_mappings is None:
        token_mappings = []

    def choose(alternatives: list[Token]):
        for ranker in token_rankers:
            alternatives = ranker.filter_best(alternatives)
            if len(alternatives) == 1:
                # no need to filter further
                break
        if len(alternatives) > 1:
            # unresolved ties
            logging.warning(f'Choosing randomly for token "{token}" from {alternatives}')
            alternatives = RandomRanker().filter_best(alternatives)
        return alternatives[0]

    normalized = dediacritise_non_malti_accents(token)
    lowered = normalized.lower()

    is_non_deterministic = len(token_rankers) > 0
    alternatives = translit_word(lowered, token_mappings, is_non_deterministic)
    alternatives = list(set(alternatives))  # filter out duplicates
    assert len(alternatives) > 0
    alternatives = [Token(transliterated_token) for transliterated_token in alternatives]

    transliterated_token = choose(alternatives) if is_non_deterministic else alternatives[0]

    return (transliterated_token.text, transliterated_token.merges_with_next) \
        if return_token_merge else \
        transliterated_token.text


def transliterate_sequence(tokens: list[str],
                           token_mappings: list[str] = None,
                           token_rankers: list[TokenRanker] = None) -> list[str]:
    """
    Transliterates a sequence of Maltese tokens to a corresponding sequence of Arabic tokens.

    :param tokens: The tokens to transliterate.
                   Each token should be tokenized with the rules in mind
                   as otherwise this might lead to different behaviour than expected.
    :param token_mappings: The token mappings to use in addition to the character mappings.
    :param token_rankers: The rankers to use when for non-deterministic character mappings.
                          The order specifies which ranker to apply first & which rankers to use for tie-breaks.
                          When tie-breaks cannot be resolved after going through all rankers,
                          these are resolved using :class:`RandomRanker`.
                          When this is unspecified, a deterministic mapping is used.
    :return: The transliterated tokens.
             The resulting sequence should be of equal length to the source sequence.
             A token can map to no tokens or multiple tokens, but the resulting element in the sequence is retrained
             in both cases, joining with a `" "` for multiple tokens.
    """

    return list(map(lambda token: transliterate(token, token_mappings, token_rankers), tokens))
