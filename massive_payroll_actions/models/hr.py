# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_cancel(self):
        self.write({'state': 'cancel'})
        self.mapped('payslip_run_id').action_close()


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection(
        selection_add=[('cancel', 'Cancelado')]
    )

    def action_cancel(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.write({'state': 'cancel'})

    def action_check(self):
        slip_ids = self.mapped('slip_ids')
        if not slip_ids:
            raise ValidationError(u'Debe generar nóminas antes de validar.')
        slip_ids.compute_sheet()
        self.write({'state': 'verify'})

    def action_draft(self):
        slip_ids = self.mapped('slip_ids')
        slip_ids.action_payslip_cancel()
        slip_ids.action_payslip_draft()
        return super(HrPayslipRun, self).action_draft()

    def action_validate(self):
        self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel').with_context(payslip_generate_pdf=True).action_payslip_done()
        self.action_close()
