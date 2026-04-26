'''
Rule-based line joiner that joins a list of text lines into a single line, adding spaces between
lines only where necessary and rejoining hyphenated words.
'''

import re
from malti.line_joiner.line_joiner import LineJoiner
from malti.data import Data


class RBLineJoiner(LineJoiner):
    '''
    Rule-based line joiner that joins a list of text lines into a single line, adding spaces between
    lines only where necessary and rejoining hyphenated words.
    '''

    def __init__(
        self,
    ) -> None:
        '''
        Initialiser.
        '''
        self.no_space_end_chars = set('-—/')
        self.last_word_re = re.compile('^.*?(?P<last_word>[a-zċġħż]*-)$', re.IGNORECASE)
        self.url_re = re.compile(
            '^.*?\\b' # Scan the line until you reach a word boundary followed by the following...
            '('
                'https?:|ftp:|www\\.' # Either a URL starter (e.g. http://google.com),
                '|\\.(com|net|org|edu)\\b' # Or a top level domain (e.g. .com)...
            ')'
            '[^ ]*-$', # Followed by non-spaces and a dash at the end of the line (e.g. .com/a-b-).
        )
        self.num_re = re.compile('^.*[0-9]+-$')

    def is_hyphenated_word_at_end(
        self,
        line: str,
    ) -> bool:
        '''
        Check if the line ends with a hyphenated (partial) word.

        :param line: The line to check.
        :return: Whether the line ends with a hyphenated word.
        '''
        if line[-1] != '-':
            return False

        # Get the last word
        match = self.last_word_re.match(line)
        assert match is not None
        last_word = match.group('last_word').lower() # Guaranteed that at least '-' will be matched.

        # If the dash is not attached to a word, nothing is hyphenated.
        if last_word == '-':
            return False

        # If last word is an expected dashed word, assume that hyphenation would
        # have been avoided as it would lead to confusion when reading (e.g. il-lum).
        if last_word in Data.get_tokens_with_dash_end():
            return False

        # Other checks

        # If dash is part of a URL, then it is not a hyphenated word.
        if self.url_re.match(line):
            return False

        # If dash is attached to a number, then it is not a hyphenated word.
        if self.num_re.match(line):
            return False

        return True

    def join_lines(
        self,
        lines: list[str],
        fix_hyphenated_words: bool = False,
    ) -> str:
        '''
        Join a list of Maltese text lines into one string, adding a space where necessary.
        Optionally, try to join hyphenated word segments back together as well.

        A space should not be put between two lines if it ends in a dash, em dash, or slash
        (for URLs), provided that the character before it is not a space.
        Examples:

        * ``['dak', 'kelb']`` -> ``'dak kelb'``
        * ``['il-', 'kelb']`` -> ``'il-kelb'``
        * ``['dak kelb -', 'litteralment']`` -> ``'dak kelb - litteralment'``
        * ``['- item 1', '- item 2']`` -> ``'- item 1 - item 2'``

        :param lines: A list of Maltese text lines.
        :param fix_hyphenated_words: Whether to try to join hyphenated word segments back
            together as well.
        :return: The joined lines.
        '''
        # Strip spaces from line edges and remove empty lines.
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != '']

        if lines == []:
            return ''

        # Add a space between lines where appropriate.
        new_lines = []
        last_line_index = len(lines) - 1
        for (i, line) in enumerate(lines):
            new_lines.append(line)
            if i == last_line_index:
                pass
            elif line[-1] in self.no_space_end_chars:
                if len(line) > 1 and line[-2] == ' ':
                    new_lines.append(' ')
                # Hyphen detection and correction
                elif fix_hyphenated_words and self.is_hyphenated_word_at_end(line):
                    new_lines.pop()
                    new_lines.append(line[:-1]) # Remove the hyphen from the line.
            else:
                new_lines.append(' ')

        return ''.join(new_lines)
