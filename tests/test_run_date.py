import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_date import context


class RunDateTests(unittest.TestCase):
    def test_cloud_utc_midnight_keeps_previous_chicago_day(self):
        value=context(dt.datetime(2026,10,10,1,33,tzinfo=dt.timezone.utc))
        self.assertEqual(value['run_date'],'2026-10-09')
        self.assertEqual(value['cover_date'],'October 9th, 2026')

    def test_winter_year_boundary_uses_central_standard_time(self):
        value=context(dt.datetime(2026,1,1,4,tzinfo=dt.timezone.utc))
        self.assertEqual(value['run_date'],'2025-12-31')
        self.assertEqual(value['cover_date'],'December 31st, 2025')

    def test_daylight_time_and_ordinal_teens(self):
        value=context(dt.datetime(2026,7,12,18,tzinfo=dt.timezone.utc))
        self.assertEqual(value['run_date'],'2026-07-12')
        self.assertEqual(value['cover_date'],'July 12th, 2026')

    def test_naive_instants_cannot_silently_use_host_timezone(self):
        with self.assertRaises(ValueError):context(dt.datetime(2026,10,10,1,33))
