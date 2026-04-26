'''
Join a list of text lines into a single line, adding spaces between lines only where necessary and
rejoining hyphenated words.
'''

from abc import ABC


class LineJoiner(ABC):
    '''
    Top-level abstract class representing all line joiners.
    '''

    def join_lines(
        self,
        lines: list[str],
        fix_hyphenated_words: bool = False,
    ) -> str:
        '''
        Join a list of Maltese text lines into one string, adding a space where necessary.
        Optionally, try to join hyphenated word segments back together as well.

        :param lines: A list of Maltese text lines.
        :param fix_hyphenated_words: Whether to try to join hyphenated word segments back
            together as well.
        :return: The joined lines.
        '''
        raise NotImplementedError()
