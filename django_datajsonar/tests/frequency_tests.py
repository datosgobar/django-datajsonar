from datetime import time, datetime

from django.test import TestCase
from freezegun import freeze_time

from django_datajsonar.frequency import get_next_run_date
from django_datajsonar import strings


@freeze_time("2019-01-01 06:00:00")  # Tuesday
class NextRunDateTests(TestCase):

    def setUp(self):
        self.now = datetime.now()  # Localtime

    def test_get_daily_next_run_date(self):

        nine_am = time(9, 0)
        next_run_date = get_next_run_date(start_time=self.now, scheduled_time=nine_am)

        self.assertEqual(next_run_date, datetime(2019, 1, 1, 9, 0, 0))

    def test_get_daily_next_run_date_for_tomorrow(self):

        before_now = time(5, 0)
        next_run_date = get_next_run_date(start_time=self.now, scheduled_time=before_now)

        self.assertEqual(next_run_date, datetime(2019, 1, 2, 5, 0, 0))

    def test_get_next_run_date_weekdays(self):

        nine_am = time(9, 0)
        week_days = [strings.MON, strings.TUE]
        next_run_date = get_next_run_date(start_time=self.now, scheduled_time=nine_am, week_days=week_days)

        self.assertEqual(next_run_date, datetime(2019, 1, 1, 9, 0, 0))  # Today is tuesday!

    def test_get_next_run_date_weekdays_not_today(self):
        nine_am = time(9, 0)
        week_days = ['MON']
        next_run_date = get_next_run_date(start_time=self.now, scheduled_time=nine_am, week_days=week_days)

        self.assertEqual(next_run_date, datetime(2019, 1, 7, 9, 0, 0))  # Next monday

    def test_iterate_next_run_dates(self):
        nine_am = time(9, 0)
        week_days = [strings.MON, strings.TUE, strings.WED, strings.THU]

        expected_dates = [  # Tuesday, Wednesday, Thursday, then next week's Monday
            datetime(2019, 1, 1, 9, 0, 0),
            datetime(2019, 1, 2, 9, 0, 0),
            datetime(2019, 1, 3, 9, 0, 0),
            datetime(2019, 1, 7, 9, 0, 0),
        ]

        start_time = self.now
        for expected_date in expected_dates:
            next_run_date = get_next_run_date(start_time=start_time, scheduled_time=nine_am, week_days=week_days)

            self.assertEqual(next_run_date, expected_date)
            start_time = next_run_date
