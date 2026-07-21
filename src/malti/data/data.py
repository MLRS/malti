'''
Data resources.
'''
import csv
import json
import os
from typing import Optional

__all__ = [
    'Data',
]


class Data:
    '''
    Singleton class for lazily loading and caching data from files.
    '''

    __tokens_with_dash_end: Optional[set[str]] = None

    @staticmethod
    def get_tokens_with_dash_end(
    ) -> set[str]:
        '''
        Get a set of common Maltese tokens that end with a dash.

        :return: The set of tokens.
        '''
        if Data.__tokens_with_dash_end is None:
            path = os.path.join(os.path.dirname(__file__), 'tokens_with_dash_end.json')
            with open(path, 'r', encoding='utf-8') as f:
                Data.__tokens_with_dash_end = set(json.load(f))
        return Data.__tokens_with_dash_end

    __token_frequencies = None

    @staticmethod
    def get_km_token_frequencies(

    ) -> dict[str, int]:
        """
        Get Maltese token frequencies according to Korpus Malti corpus.

        :return: A dictionary mapping tokens to their frequency.
        """
        if Data.__token_frequencies is None:
            with open(
                os.path.join(os.path.dirname(__file__), 'km_token_frequencies.tsv'),
                'r',
                encoding='utf-8',
            ) as file:
                Data.__token_frequencies = {
                    token: int(count)
                    for (token, count) in csv.reader(file, delimiter="\t")
                }
        return Data.__token_frequencies
