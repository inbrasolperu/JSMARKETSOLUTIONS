# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models


class HrLeaveAllocationAccrualCalculatorAccruement(models.TransientModel):
    _name = 'hr.leave.allocation.accrual.calculator.accruement'
    _description = 'HR Leave Allocation Accrual Calculator Accruement'

    calculator_id = fields.Many2one(
        string='Calculator',
        comodel_name='hr.leave.allocation.accrual.calculator',
    )
    days_accrued = fields.Float(
        string='Number of Days',
        readonly=True,
        required=True,
    )
    accrued_on = fields.Date(
        string='Accruement Date',
        readonly=True,
        required=True,
    )
    reason = fields.Char(
        string='Reason',
        readonly=True,
        required=True,
    )


class HrLeaveAllocationAccrualBalanceCalculator(models.TransientModel):
    _name = 'hr.leave.allocation.accrual.calculator'
    _description = 'HR Leave Allocation Accrual Calculator'

    date = fields.Date(
        string='Date',
        required=True,
    )
    accruement_ids = fields.One2many(
        string='Accruements',
        comodel_name=(
            'hr.leave.allocation.accrual.calculator.accruement'
        ),
        inverse_name='calculator_id',
        readonly=True,
    )
    accrued = fields.Float(
        string='Accrued',
        readonly=True,
    )
    balance = fields.Float(
        string='Balance',
        readonly=True,
    )

    @api.onchange('date')
    def _onchange(self):
        self._recalculate()

    def _recalculate(self):
        self.ensure_one()

        if not self.date:
            self.balance = 0.0
            self.accruement_ids = [(5, False, False)]
            return

        HrLeaveAllocation = self.env['hr.leave.allocation']
        leave_allocation = HrLeaveAllocation.browse(
            self.env.context.get('active_id')
        )

        accruements, accrued = leave_allocation._calculate_accrued_amount(
            datetime.combine(self.date, datetime.min.time()),
        )

        balance = 0.0
        accruement_ids = [(5, False, False)]
        for accruement in accruements:
            balance += accruement.days_accrued
            accruement_ids.append((0, 0, {
                'days_accrued': accruement.days_accrued,
                'accrued_on': accruement.accrued_on,
                'reason': accruement.reason,
            }))

        self.accrued = accrued
        self.balance = balance
        self.accruement_ids = accruement_ids
