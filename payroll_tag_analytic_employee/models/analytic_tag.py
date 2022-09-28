# coding: utf-8

from odoo import models, fields, exceptions, _
# from odoo.tools.float_utils import float_compare
# from datetime import timedelta


class AccountAnalyticTagAutomatic(models.Model):
    _inherit = 'account.analytic.tag'

    regenerated = fields.Boolean(
        string='Cuentas Analiticas Automaticas',
        help='Si el valor es True, se asignaran las cuentas analiticas en funcion al parte de horas',
        default=True
    )


class AccountAnalyticLineCalculate(models.Model):
    _inherit = 'account.analytic.line'

    def get_timesheet_for_project_mounth(self, date_begin, date_end, company_id):
        if date_begin and date_end and company_id:
            if date_begin > date_end:
                raise exceptions.ValidationError(
                    _('La fecha de inicio no puede ser mayor a la fecha final')
                )
            self.env.cr.execute(
                ''' select  employee_id, sum(unit_amount) from account_analytic_line where
                date <= %s AND date >= %s  AND company_id=%s group by employee_id''', (
                date_end, date_begin, company_id)
            )
            model_employee_ids = self.env.cr.fetchall()
            tag_ids = self.env['account.analytic.tag'].search([
                ('regenerated', '=', True),
                ('active_analytic_distribution', '=', True),
                ('active', '=', True),
                ('company_id', '=', company_id),
            ])
            if tag_ids:
                tag_ids.analytic_distribution_ids.unlink()
            for employee in model_employee_ids:
                value_to_html = self.env['ir.qweb.field.float_time'].value_to_html
                total_employee = round(float(employee[1]), 3)
                employee_id = employee[0]
                if employee_id:
                    self.env.cr.execute(
                    '''
                    select  project_id, sum(unit_amount) from account_analytic_line
                    where date <= %s AND date >= %s AND employee_id = %s  AND company_id=%s
                    group by project_id''', (date_end, date_begin, employee_id, company_id)
                    )
                    model_project_ids = self.env.cr.fetchall()
                    for project in model_project_ids:
                        project_id = project[0]
                        # value_to_html_project = self.env['ir.qweb.field.float_time'].value_to_html
                        total_employee_line = float(project[1]) if project[1] != 0.0 else 0.0
                        if total_employee == 0.0:
                            percentage = 0.0
                        else:
                            percentage = round(float(total_employee_line / total_employee) * 100, 3)
                        res_employee = self.env['hr.employee'].browse([employee_id])
                        res_project = self.env['project.project'].browse([project_id])
                        if res_employee and res_project:
                            analytic_tag = res_employee[0].account_analytic_tag_ids
                            analytic_id = res_project[0].analytic_account_id.id
                            if analytic_tag and analytic_id:
                                vars = {
                                    'tag_id': int(analytic_tag.id),
                                    'account_id': int(analytic_id),
                                    'percentage': float(percentage)
                                }
                                analytic_tag.analytic_distribution_ids.create(vars)
