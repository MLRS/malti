'''
Korpus Malti tokeniser.
'''

from malti.tokeniser.regex_tokeniser import RegexTokeniser


__all__ = [
    'KMTokeniser',
]


#######################################################
class KMTokeniser(RegexTokeniser):
    '''
    The tokeniser used by the MLRS Korpus Malti corpus.
    Taken from https://github.com/UMSpeech/MASRI/blob/main/masri/tokenise/tokenise.py
    '''

    #######################################################
    def __init__(
        self,
    ) -> None:
        '''
        Constructor.
        '''
        numeric_date = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}'
        decimal = r'\d+[.,/]\d+'
        number = r'\d+'

        def_article = r'\w{0,5}?[dtlrnsxzcżċ]-' # e.g. għall- or l-
        def_numeral = r'-i[dtlrnsxzcżċ]' # e.g. -il

        proclitic_prep = r"^\w['’]$"

        word = r'\w+[`\']?|\S'

        end_punctuation = r'\?|\.|,|\!|;|:|…|"|\'|\.\.\.\''

        super().__init__(
            '|'.join([
                numeric_date,
                decimal,
                number,
                def_article,
                def_numeral,
                proclitic_prep,
                word,
                end_punctuation,
            ])
        )
