from datetime import datetime

from croniter import croniter

from django_datajsonar.strings import SYNCHRO_DAILY_FREQUENCY


def get_next_run_date(start_time, scheduled_time, frequency):
    if frequency != SYNCHRO_DAILY_FREQUENCY:
        raise NotImplementedError

    cron_string = "{} {} * * *".format(scheduled_time.minute, scheduled_time.hour)

    return croniter(cron_string, start_time=start_time).get_next(datetime)
