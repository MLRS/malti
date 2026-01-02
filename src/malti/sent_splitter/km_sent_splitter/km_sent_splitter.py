'''
Korpus Malti sentence splitter.
'''

import os
import sentence_splitter
import malti
from malti.sent_splitter.sent_splitter import SentSplitter


__all__ = [
    'KMSentSplitter',
]


#######################################################
class KMSentSplitter(SentSplitter):
    '''
    The sentence splitter used by the MLRS Korpus Malti corpus.
    '''

    #######################################################
    def __init__(
        self,
    ) -> None:
        '''
        Constructor.
        '''
        super().__init__()
        self._spltter = sentence_splitter.SentenceSplitter(
            language='it',
            non_breaking_prefix_file=os.path.join(
                malti.path, 'sent_splitter', 'km_sent_splitter',
                'mt_non_breaking_prefixes.txt',
            ),
        )

    #######################################################
    def split(
        self,
        text: str,
    ) -> list[str]:
        '''
        Split a text into a list of sentences.

        :param text: The text to split.
        :return: The list of sentences.
        '''
        return self._spltter.split(text)
