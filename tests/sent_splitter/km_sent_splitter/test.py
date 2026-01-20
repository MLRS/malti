'''
Test the ``KMSentenceSplitter``.
'''

import os
import json
import unittest
import malti
from malti.sent_splitter import KMSentSplitter


class KMSentenceSplitterTest(unittest.TestCase):
    '''
    Test the ``KMSentenceSplitter``.
    '''

    def test_split(
        self,
    ) -> None:
        '''
        Test the KM sentence splitter's ``split`` method.
        '''
        with open(
            os.path.join(
                malti.path, '..', '..', 'tests', 'sent_splitter', 'km_sent_splitter',
                'test_set.json',
            ),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        splitter = KMSentSplitter()
        for test_item in test_set:
            output = splitter.split(test_item['text'])
            self.assertEqual(
                output,
                test_item['split'],
                msg=output,
            )


if __name__ == '__main__':
    unittest.main()
