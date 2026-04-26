'''
Test the ``RBLineJoiner``.
'''

import os
import json
import unittest
from malti.line_joiner import RBLineJoiner


class RBLineJoinerTest(unittest.TestCase):
    '''
    Test the ``RBLineJoiner``.
    '''

    def test_join_lines_no_fix_hyphen_words(
        self,
    ) -> None:
        '''
        Test the rule-based line joiner's ``join_lines`` method.
        '''
        with open(
            os.path.join(os.path.dirname(__file__), 'test_set.json'),
            'r', encoding='utf-8'
        ) as f:
            test_set = json.load(f)

        line_joiner = RBLineJoiner()
        for test_item in test_set:
            for fix_hyphenated_words in [False, True]:
                output = line_joiner.join_lines(
                    test_item['lines'],
                    fix_hyphenated_words=fix_hyphenated_words,
                )
                self.assertEqual(
                    output,
                    test_item[
                        'joined_' + ('fixed_hyphen' if fix_hyphenated_words else 'unfixed_hyphen')
                    ],
                    msg=f'fix_hyphenated_words={fix_hyphenated_words}: {output}',
                )


if __name__ == '__main__':
    unittest.main()
