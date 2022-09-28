# coding: utf-8

from odoo import api, fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def _get_supported_account_types(self):
        return [('bank', 'Normal'), ('wage', 'Sueldo'), ('cts', 'CTS'), ('other', 'Otros')]

    acc_type = fields.Selection(
        selection=lambda x: x.env['res.partner.bank'].get_supported_account_types(),
        default='bank',
        string='Type',
        help='Bank account type: Normal or IBAN. Inferred from the bank account number.',
        compute=False,
        required=False
    )
    type_bank_code = fields.Char(
        string=u'Código'
    )
    cci = fields.Char(
        string='CCI'
    )
