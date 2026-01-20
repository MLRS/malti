'''
Tokenisers for Maltese text.
'''

from malti.tokeniser.tokeniser import Tokeniser
from malti.tokeniser.regex_tokeniser import RegexTokeniser
from malti.tokeniser.km_tokeniser.km_tokeniser import KMTokeniser


def tokenise(
    text: str,
) -> list[str]:
    '''
    Default tokeniser.
    In this version, ``KMTokeniser`` is used.

    :param text: The text to tokenise.
    :return: The list of tokens.
    '''
    return KMTokeniser().tokenise(text)
