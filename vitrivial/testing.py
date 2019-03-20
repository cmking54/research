import unittest
from contour import Contour
import cv2
from tools import Tools
import numpy as np


def method_tester(function_name, inputs, outputs):  # test_method_template
    if len(inputs) != len(outputs):
        raise Exception('Tester for ' + str(function_name) + 'is improper.')
    results = []
    for a_input in inputs:
        test_image = cv2.imread(a_input)  # may be an issue
        results += [function_name(test_image)]
    if outputs is not None:
        for index in range(len(results)):
            results[index] = (results[index] == outputs[index])
    return results


"""class ContourTester(unittest.TestCase):

    def test_proper_input_contour_compute_all(self):
        test_results = method_tester(lambda x: Contour.compute_all(x, -1) is not None,
                                     ['blank_mask.png', 'elodie_mask.png'],
                                     [False, True])
        for test_result in test_results:
            self.assertTrue(test_result,
                            'Failed catching masks')
"""


class ToolTester(unittest.TestCase):

    def test_array_conversion(self):
        np_test_array = np.array([np.array([np.array([394, 102])])])
        py_test_array = [[394, 102]]
        self.assertTrue(len(np_test_array.shape) == 3, 'Sanity Check')
        # self.assertTrue(len(py_test_array.shape) == 2, 'Sanity Check')
        py_result_array = Tools.convert_array_np2py(np_test_array)
        np_result_array = Tools.convert_array_py2np(py_test_array)
        # print np_result_array
        self.assertTrue(len(np_result_array.shape) == 3, 'Dim Check: %d != 3' % (len(np_result_array.shape)))
        # self.assertTrue(len(py_result_array.shape) == 2, 'Dim Check')
        for ind in range(len(py_test_array)):
            for dim in range(2):
                self.assertTrue(np_test_array[ind][0][dim] == np_result_array[ind][0][dim], 'Should be equal')
                self.assertTrue(py_test_array[ind][dim] == py_result_array[ind][dim], 'Should be equal')


if __name__ == '__main__':
    unittest.main()
