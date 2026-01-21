'''
Korpus Malti tokeniser.
'''

import re
from malti.tokeniser.regex_tokeniser import RegexTokeniser


__all__ = [
    'KMTokeniser',
]


class KMTokeniser(RegexTokeniser):
    '''
    The tokeniser used by the MLRS Korpus Malti corpus.
    Adapted from https://github.com/UMSpeech/MASRI/blob/main/masri/tokenise/tokenise.py
    Even though the linked repository does not have an MIT license, we have permission from the
    owner, albertgatt, to include it in this MIT licensed project.
    '''

    NUMERIC_DATE = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}'
    '''Capture dates expressed numerically e.g. 10/10/2010'''

    DECIMAL = r'\d+[.,/]\d+'
    '''Captures decimal numbers e.g. 10.1'''

    NUMBER = r'\d+'
    '''Captures whole numbers e.g. 10'''

    DEF_ARTICLE = r'\w{0,5}?[dtlrnsxzcżċ]-'
    '''Captures definite articles e.g. għall- or l-'''

    DEF_NUMERAL = r'-i[dtlrnsxzcżċ]'
    '''Captures definite numerals e.g. -il (as in ħdax-il)'''

    PROCLITIC_PREP = r'^\w[\'’]$'
    '''Captures proclitic prepositions e.g. l' '''

    WORD = r'\w+[`\']?|\S'
    '''Captures words e.g. kelb'''

    END_PUNCTUATION = r'\?|\.|,|\!|;|:|…|"|\'|\.\.\.\''
    '''Captures end-of-sentence punctuation marks e.g. .'''

    ABBREV_PREFIX = r'sant[\'’]|(a\.?m|p\.?m|onor|sra|nru|dott|kap|mons|dr|prof)\.?'
    '''Captures abbreviations e.g. Sant' (as in Sant'Anna)'''

    def __init__(
        self,
    ) -> None:
        '''
        Constructor.
        '''
        super().__init__(
            '|'.join([
                self.NUMERIC_DATE,
                self.DECIMAL,
                self.NUMBER,
                self.DEF_ARTICLE,
                self.DEF_NUMERAL,
                self.PROCLITIC_PREP,
                self.WORD,
                self.END_PUNCTUATION,
            ]),
            re.UNICODE | re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        # Tokens that match this regex should not have a space AFTER them.
        self._detok_no_space_after_re = re.compile(
            f'{self.DEF_ARTICLE}|{self.PROCLITIC_PREP}|{self.ABBREV_PREFIX}',
            re.IGNORECASE
        )

        # Tokens that match this regex should not have a space BEFORE them.
        self._detok_no_space_before_re = re.compile(
            f'{self.END_PUNCTUATION}|{self.DEF_NUMERAL}',
            re.IGNORECASE
        )

    def detokenise(
        self,
        tokens: list[str],
    ) -> str:
        '''
        Detokenise the list of tokens back into a whole text.

        :param tokens: The tokenised text.
        :return: The text.
        '''
        tokens_with_spaces: list[str] = []

        for token in tokens:
            if self._detok_no_space_after_re.match(token):
                tokens_with_spaces.append(token)
            elif self._detok_no_space_before_re.match(token):
                if tokens_with_spaces and tokens_with_spaces[-1] == ' ':
                    tokens_with_spaces.pop() # Remove the previously added space (if there is one).
                    tokens_with_spaces.append(token)
                    tokens_with_spaces.append(' ')
                # Code that this was taken from did not have an `else` for the previous `if`.
            else:
                tokens_with_spaces.append(token)
                tokens_with_spaces.append(' ')

        text = ''.join(tokens_with_spaces)
        return text.strip()
