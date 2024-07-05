'''
A tokeniser.
'''

from abc import ABC


__all__ = [
    'Tokeniser',
]


#######################################################
class Tokeniser(ABC):
    '''
    Top-level abstract class representing all tokenisers.
    '''

    #######################################################
    def __init__(
        self,
    ) -> None:
        '''
        Empty constructor.
        '''

    #######################################################
    def tokenise(
        self,
        text: str,
    ) -> list[str]:
        '''
        Tokenise a text into a list of tokens.

        :param text: The text to tokenise.
        :return: The list of tokens.
        '''
        raise NotImplementedError()

    #######################################################
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
        raise NotImplementedError()
