"""Package handling tasks on Leica."""
from apscheduler.schedulers.blocking import BlockingScheduler
from briefy.leica.config import CRON_HOUR_JOB_TASKS
from briefy.leica.config import CRON_MINUTE_JOB_TASKS
from briefy.leica.log import tasks_logger as logger
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets
from briefy.leica.tasks.pool import move_assignment_to_pool


def main():
    """Initialize and execute the Leica Task Manager."""
    sched = BlockingScheduler()

    @sched.scheduled_job('cron', hour=CRON_HOUR_JOB_TASKS, minute=CRON_MINUTE_JOB_TASKS)
    def run_tasks():
        """Run all tasks."""
        move_assignment_to_pool()
        move_assignments_awaiting_assets()

    logger.info('Starting Leica Task Manager.')
    sched.start()
