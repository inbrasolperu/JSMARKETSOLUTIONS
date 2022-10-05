# coding: utf-8

from odoo import api, fields, models


class CareerLine(models.Model):
    _name = 'career.line'
    _description = 'Línea de carrera'

    movement_date = fields.Date(
        string='Fecha de Movimiento',
        required=True
    )
    job_id = fields.Many2one(
        string='Cargo',
        comodel_name='hr.job',
        required=True
    )
    wage = fields.Monetary(
        string='Sueldo',
        digits=(16, 2),
        required=True
    )
    currency_id = fields.Many2one(
        string="Currency",
        related='contract_id.currency_id',
        readonly=True
    )
    motive = fields.Char(
        string='Motivo'
    )
    contract_id = fields.Many2one(
        comodel_name='hr.contract',
        inverse_name='career_line_ids',
        string='Contrato'
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Empleado',
        related='contract_id.employee_id',
        store=True
    )

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s | %s" % (rec.job_id.name, rec.movement_date)))
        return result

    @api.model
    def create(self, vals):
        rec = super(CareerLine, self).create(vals)
        self.update_career_line_in_contract(rec.contract_id)
        return rec

    def write(self, vals):
        rec = super(CareerLine, self).write(vals)
        self.update_career_line_in_contract(self.contract_id)
        return rec

    @staticmethod
    def update_career_line_in_contract(rec):
        line = max(rec.career_line_ids, key=lambda x: x.movement_date)
        rec.job_id = rec.employee_id.job_id = line.job_id
        rec.employee_id.job_title = line.job_id.name
        rec.department_id = rec.employee_id.department_id = line.job_id.department_id
        rec.wage = line.wage
        rec.hourly_wage = line.wage
