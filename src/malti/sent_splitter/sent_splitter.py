'''
A sentence splitter.
'''

from abc import ABC


__all__ = [
    'SentSplitter',
]


class SentSplitter(ABC):
    '''
    Top-level abstract class representing all sentence splitters.
    '''

    def split(
        self,
        text: str,
    ) -> list[str]:
        '''
        Split a text into a list of sentences.

        :param text: The text to split.
        :return: The list of sentences.
        '''
        raise NotImplementedError()
