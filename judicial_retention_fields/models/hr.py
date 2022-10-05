# coding: utf-8

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    judicial_discount = fields.Float(
        string=u'Descuento judicial',
        groups="hr.group_hr_user"
    )
    judicial_discount_percent = fields.Float(
        string=u'Descuento judicial porcentaje',
        groups="hr.group_hr_user"
    )
