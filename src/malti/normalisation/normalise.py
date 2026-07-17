import logging
import re
import unicodedata

import regex as rx
from malti.data.data import Data
from malti.tokeniser import tokenise

MALTESE_CHARSET = "A-Za-zĊĠĦŻċġħżÀÈÌÒÙÁÉÍÓÚàèìòùáéíóú"
_HEURISTIC_MAPPINGS = {
    "\u00ad\u2010": "-",
    "\u00ad": "-",
    "\u2010": "-",
    "\u0006": "ċ",
    "\u0007": "ġ",
    "\u0008": "ħ",
    "\u0005": "ż",
    "\u00e6": "għ",
    "\u00c6": "GĦ",
    "\u00f0|\u00eb": "ċ",
    "\u00d0": "Ċ",
    "\u00ed|\u0101": "ġ",
    "\u00cd|\u0100": "Ġ",
    "\u00f3|\u045b": "ħ",
    "\u00d3": "Ħ",
    "\u0456|\u00fa|\u015c": "ż",
    "\u0406|\u00da": "Ż",
    "\u00c4\u008a": "ċ",
    "\u00c4\u00a1": "ġ",
    "\u00c4\u00a6": "Ħ",
    "\u00c4\u00a7": "ħ",
    "\u00c51\u20444": "ż",
    "\u7f85": "ù",
    "\u00e2\u0080\u0099": "'",
    "\u0430": "à",
    "\u0410": "À",
    "a\uf00f": "à",
    "A\uf00f": "À",
    "a`": "à",
    "A`": "À",
    "e`": "è",
    "E`": "È",
    "o`": "ò",
    "O`": "Ò",
    "u`": "ù",
    "U`": "Ù",
    "T\ufffd": "TÀ",
    "\ufffd": "à",
    "\u0092": "'",
    rf"(?<=[{MALTESE_CHARSET}])¿|¿(?=[{MALTESE_CHARSET}])": "ż",  # only when surrounded by word characters
    "`": "ċ",
    "¬": "Ċ",
    rf"(?<=[{MALTESE_CHARSET}])\[\[": "ġġ",  # same as below, but to capture doubled letters
    rf"(?<=[{MALTESE_CHARSET}])\[": "ġ",  # avoid replacing [ at the start of a word, in case it is intended as a bracket
    r"(?<=["+MALTESE_CHARSET+r"])\{\{": "ĠĠ",  # same as below, but to capture doubled letters
    r"(?<=["+MALTESE_CHARSET+r"])\{": "Ġ",  # avoid replacing { at the start of a word, in case it is intended as a bracket
    # rf"(?<=[{MALTESE_CHARSET}])\[|\[(?=[{MALTESE_CHARSET}])": "ġ",  # only when surrounded by word characters (not at the start)
    rf"\]\](?=[{MALTESE_CHARSET}])": "ħħ",  # same as below, but to capture doubled letters.
    rf"\](?=[{MALTESE_CHARSET}])": "ħ",  # avoid replacing ] at the end of a word, in case it is intended as a bracket
    r"\}\}(?=["+MALTESE_CHARSET+r"])": "ĦĦ",  # same as below, but to capture doubled letters
    r"\}(?=["+MALTESE_CHARSET+r"])": "Ħ",  # avoid replacing } at the end of a word, in case it is intended as a bracket
    # rf"(?<=[{MALTESE_CHARSET}])\]|\](?=[{MALTESE_CHARSET}])": "ħ",  # only when surrounded by word characters
    r"\\": "ż",
    r"\|": "Ż",
    "#": "ż",
    "~": "Ż",
}
_HEURISTIC_MAPPINGS2 = {
    "\u00ad": "",
    rf"(?<=[{MALTESE_CHARSET}])¿|¿(?=[{MALTESE_CHARSET}])": "à",  # only when surrounded by word characters
    "\ufffd": "'",
    "a\uf00f": "a",
    "A\uf00f": "A",
    "a`": "a'",
    "A`": "A'",
    "e`": "e'",
    "E`": "E'",
    "o`": "o'",
    "O`": "O'",
    "u`": "u'",
    "U`": "U'",
    "~": "Ċ",
}
"""
Alternative mappings, for some characters which can be mapped in more than one way.
For example no all "a`" cases map to "à" (diġà), some map to "a'" (jista')
and these would be covered by these fallback mappings.
"""
_HEURISTIC_MAPPINGS2 = _HEURISTIC_MAPPINGS | _HEURISTIC_MAPPINGS2


def apply_mappings(text: str, mapping: dict[str, str]) -> str:
    """
    :param text: The text to apply mappings on.
    :param mapping: The regex mappings (source -> target) to apply, applied in the order they are defined.
    :return: The text with all regex substitutions performed
    """
    for source, target in mapping.items():
        text = re.sub(source, target, text)
    return text


def get_token_frequencies(text: str, threshold: int) -> tuple[list[int], bool]:
    """
    Gives the token frequencies of a given text.

    :param text: The input text.
    :param threshold: A numerical threshold which is used to specify the minimum frequency each token should exceed.
    :return: A tuple containing a list with the frequencies of the tokens in the given text and
             a boolean indicating whether all counts exceed the specified threshold.
    """
    counts = [
        Data.get_token_frequencies().get(token.lower(), 0) if len(token) > 1 else 0
        for token in tokenise(text)
    ]
    return counts, all(count >= threshold for count in counts)


def fix_potentially_incorrectly_rendered_maltese_characters(
        text: str,
        threshold: int = 100,
) -> str:
    """
    Fixes characters that are known to sometimes be due to rendering issues.
    These are double-checked against token frequencies from a corpus (with a configurable `threshold`)
    to verify that substitutions result in plausible tokens.
    This function doesn't capture all cases, instead prioritising precision, so that incorrect substitutions are minimised.
    """

    text_parts = []

    # There are cases when characters are used to split words but sometimes have spaces before and after them.
    # This is problematic since there is verification on the token level, and as a result other character substitutions
    # would not take effect because the resultant partial word is not a valid full word.
    # Potential word splitter characters are transformed to a soft hyphen as a canonical form,
    # and there are then specific heuristics to map this accordingly.
    text = re.sub(r"( ¬)+ ", "\u00ad", text)
    text = re.sub(r"\s*\u00ad\s*", "\u00ad", text)

    # do not tokenise properly, in case of certain characters incorrectly splitting tokens off,
    # which would result in heuristic checks to fail later on if the sub-tokens are partial words
    for token in text.split():
        if all(len(token) == 1 for token in tokenise(token)):
            # For cases when a given text span is composed of single characters (remember we are whitespace splitting),
            # heuristics are not applied since the resultant single characters would be deemed plausible
            # (single characters often have high frequency).
            text_parts.append(token)
            continue

        normalised_token1 = apply_mappings(token, _HEURISTIC_MAPPINGS)
        normalised_token2 = apply_mappings(token, _HEURISTIC_MAPPINGS2)

        if normalised_token1 == token:  # nothing changed
            text_parts.append(token)
            continue

        # we can now tokenise safely
        normalised_counts1, is_valid1 = get_token_frequencies(normalised_token1, threshold)
        normalised_counts2, is_valid2 = get_token_frequencies(normalised_token2, threshold)
        if is_valid1 and is_valid2: # choose token based on the higher number of counts
            unnormalised_counts, is_valid = get_token_frequencies(token, threshold)
            normalised_count = sum(unnormalised_counts)
            normalised_count1 = sum(normalised_counts1)
            normalised_count2 = sum(normalised_counts2)
            if is_valid and normalised_count > normalised_count1 and normalised_count > normalised_count2:
                normalised_token = token
            else:
                normalised_token = normalised_token1 if normalised_count1 > normalised_count2 else normalised_token2
        elif is_valid1:
            normalised_token = normalised_token1
        elif is_valid2:
            normalised_token = normalised_token2
        else:
            normalised_token = token

        text_parts.append(normalised_token)
        if token != normalised_token:
            logging.info(f"Normalised \"{token}\" as \"{normalised_token}\"")
        else:
            logging.debug(f"Skipped \"{token}\" normalisation as \"{normalised_token1}\"/\"{normalised_token2}\" "
                          f"with {normalised_counts1}/{normalised_counts2}")

    return " ".join(text_parts)


def normalise(text: str, *, apply_heuristics: bool = False) -> str:
    """
    Performs character substitutions so that variations are represented with the same character.
    This avoids ambiguities when performing certain text processing which assumes certain linguistic features.
    Examples:
    * ta` -> ta'
    * diġa` -> diġà

    The optional `apply_heuristics` performs additional character substitutions based on cases where incorrectly-rendered characters were empirically observed.
    Most of these substitutions are centered around Maltese-specific characters: ċ, ġ, ħ, ż, ', & -.
    Examples:
    * ba]ar -> baħar
    * iŜda} & iżda

    :param text: The text to normalise.
    :param apply_heuristics: Optional flag to apply additional substitutions based on some known heuristics.
                             The heuristics are applied in such a way to minimise incorrect substitutions, so some cases are knowingly unhandled.
    :return: The normalised text.
    """
    normalised_text = unicodedata.normalize("NFC", text)

    if apply_heuristics:
        normalised_text = fix_potentially_incorrectly_rendered_maltese_characters(normalised_text)

    normalised_text = rx.sub(r"\p{Z}+", " ", normalised_text)  # whitespace
    normalised_text = rx.sub(r"(?![\n\r\t])\p{C}", "", normalised_text)  # control characters (except common whitespace characters)
    normalised_text = re.sub(r"[ʼ′`ˋ‛‘’ʾʿ]", "'", normalised_text)  # apostrophe
    normalised_text = re.sub(r"[“”‟″]", "\"", normalised_text)  # quotes
    normalised_text = re.sub(r"\u2010", "-", normalised_text)  # hyphen
    return normalised_text
