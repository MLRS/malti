'''
Tokeniser class for representing tokenisers that work with regular expressions.
'''

import re
from malti.tokeniser.tokeniser import Tokeniser


__all__ = [
    'RegexTokeniser',
]


class RegexTokeniser(Tokeniser):
    '''
    Tokenise a text by using regular expressions that match tokens.
    '''

    def __init__(
        self,
        pattern: str,
        flags: re.RegexFlag = (
            re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE
        ),
    ) -> None:
        '''
        Create a regular expression tokeniser from a regular expression.

        :param pattern: A string regular expression which will be compiled into
            a regular expression ``re`` object.
        :param flags: Regular expression flags to use from the ``re`` module.
        '''
        self._regex = re.compile(pattern, flags)

    def tokenise(
        self,
        text: str,
    ) -> list[str]:
        '''
        Tokenise a text into a list of tokens.

        :param text: The text to tokenise.
        :return: The list of tokens.
        '''
        return self._regex.findall(text)

    def tokenise_indices(
        self,
        text: str,
    ) -> list[tuple[int, int]]:
        '''
        Tokenise a text and return the indices of the tokens.
        A list of integer pair tuples ``[(i, j)]`` is returned such that
        ``text[i:j]`` is a token.

        :param text: The text to tokenise.
        :return: The list of tuple pairs containing integers specifying the
            locations of the tokens in the text.
        '''
        return [
            m.span()
            for m in self._regex.finditer(text)
        ]
