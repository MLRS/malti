'''
Test the ``KMTokeniser``.
'''

import os
import json
import unittest
import malti
from malti.tokeniser import KMTokeniser


#######################################################
class KMTokeniserTest(unittest.TestCase):
    '''
    Test the ``KMTokeniser``.
    '''

    #######################################################
    def test_tokenise(
        self,
    ) -> None:
        '''
        Test the KM tokeniser's ``tokenise`` method.
        '''
        with open(
            os.path.join(
                malti.path, '..', '..', 'tests', 'tokeniser', 'km_tokeniser',
                'test_set.json',
            ),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        tokeniser = KMTokeniser()
        for test_item in test_set:
            output = tokeniser.tokenise(test_item['input'])
            self.assertEqual(
                output,
                test_item['target'].split(' '),
                msg=output,
            )

    #######################################################
    def test_tokenise_indices(
        self,
    ) -> None:
        '''
        Test the KM tokeniser's ``tokenise_indices`` method.
        '''
        with open(
            os.path.join(
                malti.path, '..', '..', 'tests', 'tokeniser', 'km_tokeniser',
                'test_set.json',
            ),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        tokeniser = KMTokeniser()
        for test_item in test_set:
            indices = tokeniser.tokenise_indices(test_item['input'])
            output = [test_item['input'][i:j] for (i, j) in indices]
            self.assertEqual(
                output,
                test_item['target'].split(' '),
                msg=indices,
            )



#######################################################
if __name__ == '__main__':
    unittest.main()
