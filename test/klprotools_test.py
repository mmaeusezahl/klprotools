import unittest
import datetime
import pathlib
import tempfile
import os

import klprotools as klp

class TestDates(unittest.TestCase):
    fixed_point_datetime = datetime.datetime(2019, 9 ,13, 14, 0, 0)
    fixed_point_julian_seconds = 212435186400

    def test_julian_seconds_to_datetime(self):
        date = klp.julian_seconds_to_datetime(self.fixed_point_julian_seconds)
        self.assertEqual(date, self.fixed_point_datetime)

        with self.assertRaises(OverflowError):
            klp.julian_seconds_to_datetime(0)

    def test_datetime_to_julian_seconds(self):
        julian_seconds = klp.datetime_to_julian_seconds(
                                                      self.fixed_point_datetime)
        self.assertEqual(julian_seconds, self.fixed_point_julian_seconds)

    def test_convert_back_forth(self):
        for t in [(2019, 9 ,13, 14, 0, 0),(1995, 2 ,1, 16, 3, 35), 
                  (2030, 12 ,31, 23, 59, 59)]:
            initial_datetime = datetime.datetime(*t)
            with self.subTest(initial_datetime):
                julian_seconds =klp.datetime_to_julian_seconds(initial_datetime)
                final_datetime =klp.julian_seconds_to_datetime(julian_seconds)

                self.assertEqual(initial_datetime, final_datetime)


class TestReading(unittest.TestCase):
    def test_read_file(self):
        path = pathlib.Path(__file__).parent.absolute()\
                                     .joinpath('data')\
                                     .joinpath('0_history.dat')

        result = klp.read_file(path)
        list(result)
    
class TestWriting(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.file = os.path.join(self.test_dir.name, '0_history.dat')
		
    def tearDown(self):
        # Close the file, the directory will be removed after the test
        self.test_dir.cleanup()

    def test_write_file(self):        
        all_entries = [
            (datetime.datetime(2000, 1, 1), [(10,50),(20,50),(20,50),(30,None),
                                (20,50),(None,50),(-10,50),(20,60), (20,50)]),
            (None,                          [(35,50),(None,50),(20,50),(30,50),
                                (20,50),(20,50),(40,50),(20,50), (20,None)]),
            (datetime.datetime(2030, 9, 4), [(35,50),(None,50),(20,50),(30,50),
                                (20,50),(20,50),(20,50),(20,50), (20,None)])
                                    ]
        
        klp.write_file(self.file, all_entries)
        read_entries = list(klp.read_file(self.file, True))

        self.assertEqual(read_entries, all_entries)

    def test_incorrect_channel_number(self):
        incorrect_entries = [(datetime.datetime(2030, 9, 4), [(35,50)])]
        with self.assertRaises(ValueError):
            klp.write_file(self.file, incorrect_entries)

if __name__ == '__main__':
    unittest.main()