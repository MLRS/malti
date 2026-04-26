'''
Data resources.
'''

import os
import json
from typing import Optional


__all__ = [
    'Data',
]


class Data:
    '''
    Singleton class for lazily loading and caching data from files.
    '''

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
    __tokens_with_dash_end: Optional[set[str]] = None
