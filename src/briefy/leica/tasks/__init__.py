"""Package handling tasks on Leica."""
from apscheduler.schedulers.blocking import BlockingScheduler
from briefy.leica.config import CRON_HOUR_JOB_TASKS
from briefy.leica.config import CRON_MINUTE_JOB_TASKS
from briefy.leica.db import Session
from briefy.leica.log import tasks_logger as logger
from briefy.leica.sync import db
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets
from briefy.leica.tasks.pool import move_assignment_to_pool

import transaction


def main():
    """Initialize and execute the Leica Task Manager."""
    sched = BlockingScheduler()
    db.configure(Session)

    @sched.scheduled_job('cron', hour=CRON_HOUR_JOB_TASKS, minute=CRON_MINUTE_JOB_TASKS)
    def run_tasks():
        """Run all tasks."""
        with transaction.manager:
            logger.info('Start moving assignments to Pool.')
            move_assignment_to_pool()
            logger.info('End moving assignments to Pool.')

        with transaction.manager:
            logger.info('Start moving assignments to Awaiting Assets.')
            move_assignments_awaiting_assets()
            logger.info('End moving assignments to Awaiting Assets..')

    logger.info('Starting Leica Task Manager.')
    sched.start()
