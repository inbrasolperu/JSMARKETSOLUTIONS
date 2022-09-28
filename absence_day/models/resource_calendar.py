from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY
from pytz import timezone
from odoo import _, api, fields, models
from odoo.addons.resource.models.resource import float_to_time, Intervals
from odoo.osv import expression
import math


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _day_off_intervals(self, start_dt, end_dt, resource=None, domain=None, tz=None):
        """ Return the attendance intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the resource's timezone.
        """
        assert start_dt.tzinfo and end_dt.tzinfo
        combine = datetime.combine

        resource_ids = [resource.id, False] if resource else [False]
        domain = domain if domain is not None else []
        domain = expression.AND([domain, [
            ('calendar_id', '=', self.id),
            ('resource_id', 'in', resource_ids),
            ('display_type', '=', False),
        ]])

        tz = tz if tz else timezone((resource or self).tz)
        start_dt = start_dt.astimezone(tz)
        end_dt = end_dt.astimezone(tz)

        result = []
        calendar_attendance_model = self.env['resource.calendar.attendance']
        attendance_ids = calendar_attendance_model.search(domain)
        days = attendance_ids.mapped('dayofweek')
        dayofweek = ['0', '1', '2', '3', '4', '5', '6']
        days_off = list(set(dayofweek) - set(days))
        days_off.sort()

        for off in days_off:
            start = start_dt.date()
            until = end_dt.date()

            if off:
                start_week_type = int(math.floor((start.toordinal() - 1) / 7) % 2)
                if start_week_type != int(off):
                    start = start + relativedelta(weeks=-1)
            weekday = int(off)

            if self.two_weeks_calendar and off:
                days = rrule(WEEKLY, start, interval=2, until=until, byweekday=weekday)
            else:
                days = rrule(DAILY, start, until=until, byweekday=weekday)

            for day in days:
                dt0 = tz.localize(combine(day, float_to_time(0.0)))
                dt1 = tz.localize(combine(day, float_to_time(8.0)))
                result.append((max(start_dt, dt0), min(end_dt, dt1), calendar_attendance_model))
        return Intervals(result)
