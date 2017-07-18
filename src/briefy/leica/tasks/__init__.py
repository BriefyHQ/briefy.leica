"""Package handling tasks on Leica."""
from apscheduler.schedulers.blocking import BlockingScheduler
from briefy.leica.config import CRON_HOUR_JOB_TASKS
from briefy.leica.config import CRON_MINUTE_JOB_TASKS
from briefy.leica.config import BEFORE_SHOOTING_SECONDS
from briefy.leica.config import LATE_SUBMISSION_SECONDS
from briefy.leica.db import db_configure
from briefy.leica.db import Session
from briefy.leica.log import tasks_logger as logger
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets
from briefy.leica.tasks.assignment import notify_before_shooting
from briefy.leica.tasks.assignment import notify_late_submissions
from briefy.leica.tasks.order import move_orders_accepted
from briefy.leica.tasks.pool import move_assignments_to_pool

import transaction


def main():
    """Initialize and execute the Leica Task Manager."""
    sched = BlockingScheduler()
    db_configure(Session)

    @sched.scheduled_job('cron', hour=CRON_HOUR_JOB_TASKS, minute=CRON_MINUTE_JOB_TASKS)
    def run_tasks():
        """Run all tasks."""
        with transaction.manager:
            logger.info('Start: moving assignments to Pool.')
            move_assignments_to_pool()
            logger.info('End: moving assignments to Pool.')

        with transaction.manager:
            logger.info('Start: moving assignments to Awaiting Assets.')
            move_assignments_awaiting_assets()
            logger.info('End: moving assignments to Awaiting Assets.')

        with transaction.manager:
            seconds = BEFORE_SHOOTING_SECONDS
            logger.info(f'Start: notifying assignments {seconds} seconds before shooting.')
            notify_before_shooting()
            logger.info(f'End: notifying assignments {seconds} seconds before shooting.')

        with transaction.manager:
            seconds = LATE_SUBMISSION_SECONDS
            logger.info(f'Start: notifying assignments not submitted '
                        f'{seconds} seconds after shooting.')
            notify_late_submissions()
            logger.info(f'End: notifying assignments not submitted '
                        f'{seconds} seconds after shooting.')

        with transaction.manager:
            logger.info('Start: moving orders to accepted.')
            move_orders_accepted()
            logger.info('End: moving orders to accepted.')

    logger.info('Starting Leica Task Manager.')
    sched.start()
