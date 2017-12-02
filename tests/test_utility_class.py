import unittest
import os, sys

dir = os.path.dirname(__file__)
filename = os.path.join(dir, '../')
sys.path.append(filename)

import utilities as ut

test_dict_1 = {"test_type:apple" :"values"}
test_dict_2 = {}

class test_strip_dictionary(unittest.TestCase):

    def test_strip_dictionary_simple(self):
        stripped_dict = ut.strip_dictionary(test_dict_1, "test_type")
        self.assertEqual(stripped_dict, {})

    def test_abs_path_with_dot_dot(self):
        self.assertEqual(ut.abs_path("../tests/hi.hi"), ut.abs_path("hi.hi"))

if __name__ == '__main__':
    unittest.main()
