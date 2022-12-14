# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _action_create_account_move(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for payslip in self:
            if not payslip.struct_id:
                raise ValidationError(_('One of the contract for these payslips has no structure type.'))
            if not payslip.struct_id.journal_id:
                raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

            # Map all payslips by structure journal and pay slips month.
            # {'journal_id': {'month': [slip_ids]}}
            slip_mapped_data = {payslip.struct_id.journal_id.id: {fields.Date().end_of(payslip.date_to, 'month'): self.env['hr.payslip']}}
            slip_mapped_data[payslip.struct_id.journal_id.id][fields.Date().end_of(payslip.date_to, 'month')] |= payslip

            for journal_id in slip_mapped_data:  # For each journal_id.
                for slip_date in slip_mapped_data[journal_id]:  # For each month.
                    line_ids = []
                    debit_sum = 0.0
                    credit_sum = 0.0
                    date = slip_date
                    move_dict = {
                        'narration': '',
                        'journal_id': journal_id,
                        'date': date,
                        'ref': payslip.number
                    }

                    for slip in slip_mapped_data[journal_id][slip_date]:
                        move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                        move_dict['narration'] += '\n'
                        for line in slip.line_ids.filtered(lambda line: line.category_id):
                            amount = -line.total if slip.credit_note else line.total
                            if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                                for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                    if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                        if amount > 0:
                                            amount -= abs(tmp_line.total)
                                        elif amount < 0:
                                            amount += abs(tmp_line.total)
                            if float_is_zero(amount, precision_digits=precision):
                                continue
                            debit_account_id = line.salary_rule_id.account_debit.id
                            credit_account_id = line.salary_rule_id.account_credit.id

                            if debit_account_id:  # If the rule has a debit account.
                                debit = amount if amount > 0.0 else 0.0
                                credit = -amount if amount < 0.0 else 0.0

                                debit_line = self._get_existing_lines(line_ids, line, debit_account_id, debit, credit)

                                if not debit_line:
                                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                                    debit_line['partner_id'] = payslip.employee_id.address_home_id.id
                                    line_ids.append(debit_line)
                                else:
                                    debit_line['debit'] += debit
                                    debit_line['credit'] += credit

                            if credit_account_id:  # If the rule has a credit account.
                                debit = -amount if amount < 0.0 else 0.0
                                credit = amount if amount > 0.0 else 0.0
                                credit_line = self._get_existing_lines(
                                    line_ids, line, credit_account_id, debit, credit)

                                if not credit_line:
                                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                                    credit_line['partner_id'] = payslip.employee_id.address_home_id.id
                                    line_ids.append(credit_line)
                                else:
                                    credit_line['debit'] += debit
                                    credit_line['credit'] += credit

                    for line_id in line_ids:  # Get the debit and credit sum.
                        debit_sum += line_id['debit']
                        credit_sum += line_id['credit']

                    # The code below is called if there is an error in the balance between credit and debit sum.
                    if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                        acc_id = slip.journal_id.default_credit_account_id.id
                        if not acc_id:
                            raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                        existing_adjustment_line = (
                            line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                        )
                        adjust_credit = next(existing_adjustment_line, False)

                        if not adjust_credit:
                            adjust_credit = {
                                'name': _('Adjustment Entry'),
                                'partner_id': payslip.employee_id.address_home_id.id,
                                'account_id': acc_id,
                                'journal_id': slip.journal_id.id,
                                'date': date,
                                'debit': 0.0,
                                'credit': debit_sum - credit_sum,
                            }
                            line_ids.append(adjust_credit)
                        else:
                            adjust_credit['credit'] = debit_sum - credit_sum

                    elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                        acc_id = slip.journal_id.default_debit_account_id.id
                        if not acc_id:
                            raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                        existing_adjustment_line = (
                            line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                        )
                        adjust_debit = next(existing_adjustment_line, False)

                        if not adjust_debit:
                            adjust_debit = {
                                'name': _('Adjustment Entry'),
                                'partner_id': payslip.employee_id.address_home_id.id,
                                'account_id': acc_id,
                                'journal_id': slip.journal_id.id,
                                'date': date,
                                'debit': credit_sum - debit_sum,
                                'credit': 0.0,
                            }
                            line_ids.append(adjust_debit)
                        else:
                            adjust_debit['debit'] = credit_sum - debit_sum

                    # Add accounting lines in the move
                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self.env['account.move'].create(move_dict)
                    for slip in slip_mapped_data[journal_id][slip_date]:
                        slip.write({
                            'move_id': move.id,
                            'date': date,
                        })
        return True
