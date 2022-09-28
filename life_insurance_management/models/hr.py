# coding: utf-8

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    life_insurance = fields.Boolean(
        string=u'Seguro de vida?',
        groups="hr.group_hr_user"
    )
    life_insurance_id = fields.Many2one(
        comodel_name='life.insurance',
        inverse_name='employees_ids',
        string=u'Póliza seguro de vida',
        groups="hr.group_hr_user"
    )
