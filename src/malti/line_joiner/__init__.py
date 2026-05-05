'''
Line joiners for Maltese text.
'''

from malti.line_joiner.line_joiner import LineJoiner
from malti.line_joiner.rb_line_joiner.rb_line_joiner import RBLineJoiner


def join_lines(
    lines: list[str],
    fix_hyphenated_words: bool = False,
) -> str:
    '''
    Default line joiner.
    In this version, ``RBLineJoiner`` is used.

    :param lines: A list of Maltese text lines.
    :param fix_hyphenated_words: Whether to try to join hyphenated word segments back
        together as well.
    :return: The joined lines.
    '''
    return RBLineJoiner().join_lines(
        lines,
        fix_hyphenated_words,
    )
