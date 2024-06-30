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
    The tokeniser used for the MLRS Korpus Malti corpus.
    '''

    #######################################################
    def __init__(
        self,
    ) -> None:
        '''
        Constructor.
        '''
        numeric_date = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}'

        decimal = r'\d+[\.,/]\d+'

        number = r'\d+'

        # Definite article + prepositions with cliticised article.
        def_article = r'\w{0,5}?[dtlrnsxzcżċ]-'
        def_numeral = r'-i[dtlrnsxzcżċ]'

        proclitic_prep = r"^\w['’]$"

        # All other tokens: string of alphanumeric chars, numbers or a single
        # non-alphanumeric char (accent or apostrophe allowed at end of string
        # of alpha chars).
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
