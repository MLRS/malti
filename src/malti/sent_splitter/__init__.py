'''
Sentence splitters for Maltese text.
'''

from malti.sent_splitter.sent_splitter import SentSplitter
from malti.sent_splitter.km_sent_splitter.km_sent_splitter import KMSentSplitter


def split(
    text: str,
) -> list[str]:
    '''
    Default sentence splitter.
    In this version, ``KMSentenceSplitter`` is used.

    :param text: The text to split.
    :return: The list of sentences.
    '''
    return KMSentSplitter().split(text)
