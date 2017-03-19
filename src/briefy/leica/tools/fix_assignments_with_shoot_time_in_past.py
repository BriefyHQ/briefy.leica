"""Fix shoot time in past."""
from briefy.leica.db import Session
from briefy.leica.sync.db import configure
from briefy.leica.tasks.assignment import move_assignments_awaiting_assets
from briefy.leica.models import Assignment
from dateutil.parser import parse
from datetime import timedelta


import pytz
import transaction

pm_tzinfo = pytz.timezone('Europe/Berlin')


class AssignmentShootTimeFix:
    """Fix assignment with shoot time wrong or in the past."""

    def __init__(self, slug, shoot_time):
        """Initialize the fix."""
        self.assignment = Assignment.query().filter_by(
            slug=slug
        ).one()
        shoot_time = parse(shoot_time)
        timezone = self.assignment.timezone
        self.shoot_time = shoot_time.replace(tzinfo=timezone)

    @property
    def project_manager(self):
        """Assinment PM uuid."""
        return str(self.assignment.project_manager)

    def _schedule(self):
        """Transition schedule."""
        assignment = self.assignment
        if assignment.state == 'assigned':
            assignment.state = 'scheduled'
            assignment_state_history = assignment.state_history.copy()
            delta = timedelta(days=1)
            trasition_date = (self.shoot_time - delta).astimezone(tz=pm_tzinfo)
            new_history = {
                'actor': self.project_manager,
                'date': trasition_date.isoformat(),
                'from': 'assigned',
                'to': 'scheduled',
                'transition': 'schedule',
                'message': 'Fixed using data fix script.'
            }
            assignment_state_history.append(new_history)
            assignment.state_history = assignment_state_history

        order = assignment.order
        if order.state == 'assigned':
            order.state = 'scheduled'
            order_state_history = order.state_history.copy()
            new_history = {
                'actor': self.project_manager,
                'date': trasition_date.isoformat(),
                'from': 'assigned',
                'to': 'scheduled',
                'transition': 'schedule',
                'message': 'Fixed using data fix script.'
            }
            order_state_history.append(new_history)
            order.state_history = order_state_history

    def __call__(self, shoot_time_only=False):
        """Execute the fix."""
        self.assignment.scheduled_datetime = self.shoot_time
        if not shoot_time_only:
            self._schedule()
        move_assignments_awaiting_assets()


if __name__ == '__main__':
    configure(Session)
    with transaction.manager:
        fixer01 = AssignmentShootTimeFix(
            slug='1701-PS6-531_03',
            shoot_time='2017-03-07 14:00:00'
        )
        fixer01()

        # fixer02 = AssignmentShootTimeFix(
        #    slug='1701-PS6-347_01',
        #    shoot_time='2017-03-02 11:00:00'
        # )
        # fixer02(shoot_time_only=True)