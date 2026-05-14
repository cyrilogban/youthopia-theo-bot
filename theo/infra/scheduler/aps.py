from apscheduler.schedulers.background import BackgroundScheduler
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

NIGERIA_TIMEZONE = ZoneInfo("Africa/Lagos")

# Calendar summary scheduled for 1:00 AM
CALENDAR_SEND_HOUR = 1
CALENDAR_SEND_MINUTE = 0

# VOTD scheduled for 6:00 AM
VOTD_SEND_HOUR = 6
VOTD_SEND_MINUTE = 0


def start_scheduler(calendar_job_func, votd_job_func):
    scheduler = BackgroundScheduler(timezone=NIGERIA_TIMEZONE)

    # 1. Calendar Job
    scheduler.add_job(
        calendar_job_func,
        "cron",
        hour=CALENDAR_SEND_HOUR,
        minute=CALENDAR_SEND_MINUTE,
        id="daily_calendar_delivery",
        replace_existing=True,
    )

    # 2. VOTD Job
    scheduler.add_job(
        votd_job_func,
        "cron",
        hour=VOTD_SEND_HOUR,
        minute=VOTD_SEND_MINUTE,
        id="daily_votd_delivery",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started. Calendar at {CALENDAR_SEND_HOUR:02d}:{CALENDAR_SEND_MINUTE:02d}, "
        f"VOTD at {VOTD_SEND_HOUR:02d}:{VOTD_SEND_MINUTE:02d} Africa/Lagos."
    )

    return scheduler
