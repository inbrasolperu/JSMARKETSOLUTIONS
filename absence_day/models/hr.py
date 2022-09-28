from datetime import datetime, date
from odoo import api, fields, models
import pytz
from dateutil.relativedelta import relativedelta


class HRContractUpdateWizard(models.TransientModel):
    _name = "hr.contract.update.wizard"
    _description = "Wizard to update fields on contracts"

    date_generated_from = fields.Date(
        string='Desde',
        required=True
    )
    date_generated_to = fields.Date(
        string='hasta',
        required=True
    )

    def action_update_hr_contract_fields(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        contract_ids = self.env['hr.contract'].browse(active_ids)
        contract_ids._generate_work_entries_specific_period(self.date_generated_from, self.date_generated_to)


class HRContract(models.Model):
    _inherit = "hr.contract"

    def _get_work_entries_values(self, date_start, date_stop):
        """
        Generate a work_entries list between date_start and date_stop for one contract.
        :return: list of dictionnary.
        """
        default_work_entry_type = self.structure_type_id.default_work_entry_type_id
        vals_list = []

        for contract in self:
            contract_vals = []
            employee = contract.employee_id
            calendar = contract.resource_calendar_id
            resource = employee.resource_id
            tz = pytz.timezone(calendar.tz)

            attendances = calendar._work_intervals(
                pytz.utc.localize(date_start) if not date_start.tzinfo else date_start,
                pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop,
                resource=resource, tz=tz
            )

            # Attendances
            for interval in attendances:
                work_entry_type_id = interval[2].mapped('work_entry_type_id')[:1] or default_work_entry_type
                # All benefits generated here are using datetimes converted from the employee's timezone
                contract_vals += [{
                    'name': "%s: %s" % (work_entry_type_id.name, employee.name),
                    'date_start': interval[0].astimezone(pytz.utc).replace(tzinfo=None),
                    'date_stop': interval[1].astimezone(pytz.utc).replace(tzinfo=None),
                    'work_entry_type_id': work_entry_type_id.id,
                    'employee_id': employee.id,
                    'contract_id': contract.id,
                    'company_id': contract.company_id.id,
                    'state': 'draft',
                }]

            # Leaves
            leaves = self.env['resource.calendar.leaves'].sudo().search([
                ('resource_id', 'in', [False, resource.id]),
                ('calendar_id', '=', calendar.id),
                ('date_from', '<', date_stop),
                ('date_to', '>', date_start)
            ])

            for leave in leaves:
                start = max(leave.date_from, datetime.combine(contract.date_start, datetime.min.time()))
                end = min(leave.date_to, datetime.combine(contract.date_end or date.max, datetime.max.time()))
                if leave.holiday_id:
                    work_entry_type = leave.holiday_id.holiday_status_id.work_entry_type_id
                else:
                    work_entry_type = leave.mapped('work_entry_type_id')
                contract_vals += [{
                    'name': "%s%s" % (work_entry_type.name + ": " if work_entry_type else "", employee.name),
                    'date_start': start,
                    'date_stop': end,
                    'work_entry_type_id': work_entry_type.id,
                    'employee_id': employee.id,
                    'leave_id': leave.holiday_id and leave.holiday_id.id,
                    'company_id': contract.company_id.id,
                    'state': 'draft',
                    'contract_id': contract.id,
                }]

            # Days off
            days_off = calendar._day_off_intervals(
                pytz.utc.localize(date_start) if not date_start.tzinfo else date_start,
                pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop,
                resource=resource, tz=tz
            )
            hr_work_entry_type_ddo = self.env.ref('absence_day.hr_work_entry_type_ddo')
            for interval in days_off:
                d1 = interval[0].astimezone(pytz.utc).replace(tzinfo=None)
                d2 = interval[1].astimezone(pytz.utc).replace(tzinfo=None)

                exits = list(filter(lambda x: x['date_start'] <= d1 <= x['date_stop'] or x['date_start'] <= d2 <= x['date_stop'], contract_vals))
                if not exits:
                    contract_vals += [{
                        'name': "%s: %s" % (hr_work_entry_type_ddo.name, employee.name),
                        'date_start': d1,
                        'date_stop': d2,
                        'work_entry_type_id': hr_work_entry_type_ddo.id,
                        'employee_id': employee.id,
                        'contract_id': contract.id,
                        'company_id': contract.company_id.id,
                        'state': 'draft',
                    }]
            # If we generate work_entries which exceeds date_start or date_stop, we change boundaries on contract
            if contract_vals:
                date_stop_max = max([x['date_stop'] for x in contract_vals])
                if date_stop_max > contract.date_generated_to:
                    contract.date_generated_to = date_stop_max

                date_start_min = min([x['date_start'] for x in contract_vals])
                if date_start_min < contract.date_generated_from:
                    contract.date_generated_from = date_start_min

            vals_list += contract_vals

        return vals_list

    def action_open_hr_contract_update_wizard(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        return {
            'context': self.env.context,
            'name': 'Actualizar campos en contrato',
            'res_model': 'hr.contract.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _generate_work_entries_specific_period(self, date_start, date_stop):
        active_ids = self.env.context.get('active_ids')
        vals_list = []
        date_start_dt = fields.Datetime.to_datetime(date_start)
        date_stop_dt = datetime.combine(fields.Datetime.to_datetime(date_stop), datetime.max.time())
        for contract in self:
            if contract.date_end:
                contract_date_end = datetime.combine(fields.Datetime.to_datetime(contract.date_end), datetime.max.time())
                date_stop = contract_date_end if date_stop_dt > contract_date_end else date_stop_dt
            else:
                date_stop = date_stop_dt
            contract.write({'date_generated_to': date_stop})
            contract_date_start = fields.Datetime.to_datetime(contract.date_start)
            date_start = contract_date_start if date_start_dt < contract_date_start else date_start_dt
            vals_list.extend(contract._get_work_entries_values(date_start, date_stop))

        if not vals_list:
            return self.env['hr.work.entry']

        for work_entry in vals_list:
            if self.env['hr.work.entry'].search([
                ('employee_id', '=', work_entry['employee_id']),
                ('date_start', '=', work_entry['date_start']),
                ('date_stop', '=', work_entry['date_stop'])
            ]):
                continue
            else:
                self.env['hr.work.entry'].create(work_entry)
        return

    def generate_work_entries_cron_method(self):
        now = datetime.now()
        init_date = datetime(now.year, now.month, 1).date()
        last_day = (datetime.now() + relativedelta(day=1, months=+1, days=-1)).date()
        contract_ids = self.env['hr.contract'].search([
            ('state', '=', 'open')
        ])
        contract_ids._generate_work_entries_specific_period(init_date, last_day)


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'

    name = fields.Char(translate=True)
