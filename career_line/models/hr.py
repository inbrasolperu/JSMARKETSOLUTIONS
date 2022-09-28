# coding: utf-8

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    career_line_ids = fields.One2many(
        comodel_name='career.line',
        inverse_name='contract_id',
        string=u'Línea de Carrera',
        copy=True
    )
    wage = fields.Monetary(required=False)
