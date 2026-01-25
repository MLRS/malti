'''
Test the ``KMTokeniser``.
'''

import os
import json
import unittest
from malti.tokeniser import KMTokeniser


class KMTokeniserTest(unittest.TestCase):
    '''
    Test the ``KMTokeniser``.
    '''

    def test_tokenise(
        self,
    ) -> None:
        '''
        Test the KM tokeniser's ``tokenise`` method.
        '''
        with open(
            os.path.join(os.path.dirname(__file__), 'test_set.json'),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        tokeniser = KMTokeniser()
        for test_item in test_set:
            output = tokeniser.tokenise(test_item['text'])
            self.assertEqual(
                output,
                test_item['tokenised'].split(' '),
                msg=output,
            )

    def test_tokenise_indices(
        self,
    ) -> None:
        '''
        Test the KM tokeniser's ``tokenise_indices`` method.
        '''
        with open(
            os.path.join(os.path.dirname(__file__), 'test_set.json'),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        tokeniser = KMTokeniser()
        for test_item in test_set:
            indices = tokeniser.tokenise_indices(test_item['text'])
            output = [test_item['text'][i:j] for (i, j) in indices]
            self.assertEqual(
                output,
                test_item['tokenised'].split(' '),
                msg=indices,
            )

    def test_detokenise(
        self,
    ) -> None:
        '''
        Test the KM tokeniser's ``detokenise`` method.
        '''
        with open(
            os.path.join(os.path.dirname(__file__), 'test_set.json'),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        tokeniser = KMTokeniser()
        for test_item in test_set:
            output = tokeniser.detokenise(test_item['tokenised'].split(' '))
            self.assertEqual(
                output,
                test_item['detokenised'],
                msg=output,
            )


if __name__ == '__main__':
    unittest.main()
