import unittest
from hanukkah_christmas_date import hanukkah_gregorian_date, notable_hanukkah_years, main, plot_date_distribution, plot_dow_distribution
from convertdate import hebrew
from pyluach import dates, hebrewcal, parshios
import datetime
import calendar
import math
from pprint import pprint
from tqdm import tqdm
import statistics
import shelve


class HanukkahDateTests(unittest.TestCase):

    def test_main(self):
        main()

    def test_chart_by_date(self):
        notable = notable_hanukkah_years(limit=1451)
        plot_date_distribution(notable['by_date'])
    def test_chart_by_dow(self):
        notable = notable_hanukkah_years()
        plot_dow_distribution(notable['by_dow'])

    def test_hanukkah_date_year_with_no_hanukkah(self):
        uut = hanukkah_gregorian_date(3031)
        self.assertEqual([], uut)
        uut = hanukkah_gregorian_date(3183)
        print(uut)
        self.assertEqual([datetime.date(3032, 1, 1), datetime.date(3032, 12, 19)], uut)

    def test_hanukkah_date_2024(self):
        uut = hanukkah_gregorian_date(2024)
        self.assertEqual([datetime.date(2024, 12, 26)], uut)

    def test_hanukkah_christmas_coincidince(self):
        notable = notable_hanukkah_years(limit=1500)
        self.assertTrue('by_date' in notable)
        self.assertTrue(2024 in notable['christmas_day'])
        self.assertTrue(3031 in notable['no_hanukkah'])


if __name__ == '__main__':
    unittest.main()
