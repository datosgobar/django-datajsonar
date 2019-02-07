from datetime import datetime

from croniter import croniter


def get_next_run_date(start_time, scheduled_time, week_days=None):
    if not week_days:
        week_days_field = "*"
    else:
        week_days_field = ','.join(week_days)

    cron_string = "{} {} * * {}".format(
        scheduled_time.minute,
        scheduled_time.hour,
        week_days_field
    )

    return croniter(cron_string, start_time=start_time).get_next(datetime)
