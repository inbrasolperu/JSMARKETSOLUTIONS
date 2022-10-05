# coding: utf-8

from odoo import api, fields, models


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def clean_employees(self):
        self.ensure_one()
        self.employee_ids = False
        self.name = "Generar Nóminas"
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
