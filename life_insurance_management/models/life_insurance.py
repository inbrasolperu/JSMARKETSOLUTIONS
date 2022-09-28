# coding: utf-8

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LifeInsurance(models.Model):
    _name = 'life.insurance'
    _description = 'Vida ley'

    name = fields.Char(
        string=u'Entidad',
        required=True
    )
    nro = fields.Char(
        string=u'N° Póliza'
    )
    start_date = fields.Date(
        string='Fecha inicio vigencia'
    )
    end_date = fields.Date(
        string='Fecha fin vigencia'
    )
    hiring_term = fields.Char(
        string=u'Plazo de contratación'
    )
    rate = fields.Float(
        string='Tasa',
        digits=(16, 4),
    )
    amount = fields.Float(
        string='Importe'
    )
    employees_ids = fields.One2many(
        comodel_name='hr.employee',
        inverse_name='life_insurance_id',
        string='Empleados'
    )
