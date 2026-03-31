from apscheduler.schedulers.background import BackgroundScheduler
import logging
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

NIGERIA_TIMEZONE = ZoneInfo("Africa/Lagos")
DAILY_SEND_HOUR = 6
DAILY_SEND_MINUTE = 0



def start_scheduler(job_func):
    scheduler = BackgroundScheduler(timezone=NIGERIA_TIMEZONE)

    scheduler.add_job(
        job_func,
        "cron",
        hour=DAILY_SEND_HOUR,
        minute=DAILY_SEND_MINUTE,
        id="daily_votd_delivery",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started for daily VOTD at 06:00 Africa/Lagos.")

    return scheduler
