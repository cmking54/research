import unittest
import application
import app_error


class AppTest(unittest.TestCase):

    def test_no_vid_source_int(self):
        result = False
        try:
            app = application.Application(5)
        except app_error.AppError:
            result = True
        self.assertTrue(result,
                         msg='Does not recognise bad int vid source')

    def test_no_vid_source_str(self):
        result = False
        try:
            app = application.Application('')
        except app_error.AppError:
            result = True
        self.assertTrue(result,
                         msg='Does not recognise bad str vid source')

if __name__ == '__main__':
    unittest.main()
