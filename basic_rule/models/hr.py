from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'

    advance_percent = fields.Float(
        string='Porcentaje de Anticipo'
    )


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    apply_advance_payroll = fields.Boolean(string='¿Aplica nómina de adelanto?')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_order_periods(self, periods):
        """
        :param periods: list of periods with this string format: mm/YYYY
        :return: list of ordered periods
        """
        new_periods = []
        for period in periods:
            _, last_day = self.env['hr.payslip'].get_month_day_range(period)
            new_periods.append(last_day)
        new_periods.sort()
        periods = [val.strftime('%m/%Y') for val in new_periods]
        return periods

    def _get_base_local_dict(self):
        """
        Pass hr.payslip id to specific searches in computed rule
        """

        res = super()._get_base_local_dict()
        res.update({
            'slip_id': self._origin.id
        })
        return res

    @staticmethod
    def _get_month(year, month, value_month):
        value = month - value_month
        if value < 0:
            new_month = 12 + value
            new_year = year - 1
        elif value == 0:
            new_month = 12
            new_year = year - 1
        else:
            new_month = value
            new_year = year
        return new_month, new_year

    @staticmethod
    def _get_periods(start_m, start_y, end_m, end_y):
        """
        :param start_m: Initial month of period
        :param start_y: Initial year of period
        :param end_m: Final month of period
        :param end_y: Final year of period
        :return: Return list of months between 'start_m/star_y' and 'end_m/end_y' => Ex: 08/18 12/18 = [08/18, 09/18, 10/18, 11/18, 12/18]
        """
        start = '{}/{}'.format("{:02d}".format(start_m), start_y)
        end = '{}/{}'.format("{:02d}".format(end_m), end_y)
        periods = [start]
        value = False
        if start == end:
            return periods
        while value != end:
            if start_y == end_y:
                start_m += 1
            else:
                start_m += 1
                if start_m == 13:
                    start_y += 1
                    start_m = 1
            value = '{}/{}'.format("{:02d}".format(start_m), start_y)
            periods.append(value)
        return periods

    def _get_months_before(self, months_before):
        month = int(self.month)
        year = int(self.year)
        start_m, star_y = self._get_month(year, month, months_before)
        end_m, end_y = self._get_month(year, month, 1)
        periods = self._get_periods(start_m, star_y, end_m, end_y)
        return periods

    @staticmethod
    def get_month_day_range(period):
        """
        :param period: month with format : mm/YYYY => Ex: 06/20
        :return: Return initial and final date of some period
        """
        datetime_str = '{}-{}-01 15:00:00'.format(period[3:], period[0:2])
        datetime_object = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').date()
        last_day = datetime_object + relativedelta(day=1, months=+1, days=-1)
        first_day = datetime_object + relativedelta(day=1)
        return first_day, last_day

    def get_inputs_data(self):
        res = super(HrPayslip, self).get_inputs_data()
        if not res:
            return res

        advance_percent = self.contract_id.advance_percent
        for r in res:
            if r['code'] == 'NQA_001' and r['contract_id'] == self.contract_id.id:
                r['amount'] = advance_percent
        return res
