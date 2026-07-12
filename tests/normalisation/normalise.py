import os
import json
import unittest
from malti.normalisation import normalise


class NormalisationTest(unittest.TestCase):

    def test_normalise(
        self,
    ) -> None:
        with open(os.path.join(os.path.dirname(__file__), "normalise_test_cases.json"), "r", encoding="utf-8") as file:
            test_set = json.load(file)

        for test_item in test_set:
            with self.subTest(**test_item, apply_heuristics=True):
                output = normalise(test_item["input"], apply_heuristics=True)
                expected_output = test_item["output"]
                self.assertEqual(output, expected_output, test_item.get("comment"))

            with self.subTest(**test_item, apply_heuristics=False):
                # heuristics shouldn't be applied, so input should stay the same
                output = normalise(test_item["input"], apply_heuristics=False)
                expected_output = test_item.get("output_no_heuristics", test_item["output"])
                self.assertEqual(output, expected_output, test_item.get("comment"))


if __name__ == '__main__':
    unittest.main()
