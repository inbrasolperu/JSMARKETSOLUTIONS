# coding: utf-8
from .reports import BankReportTxt
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import base64
import pytz

type_payment = [
    ('wage', 'Sueldo'),
    ('cts', 'CTS')
]


class HrMassivePayment(models.Model):
    _name = 'hr.massive.payment'
    _description = 'HR - Pago Masivo'

    payment_date = fields.Date(
        string='Fecha de pago',
        required=True
    )
    acc_type = fields.Selection(
        selection=type_payment,
        string='Tipo de Pago',
        required=True
    )
    exchange_type = fields.Float(
        string='Tipo de cambio'
    )
    payment_type_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Cuenta de la empresa',
        required=True
    )
    is_validate_account = fields.Boolean(
        string='¿Válida cuentas del mismo banco?'
    )
    payslip_ids = fields.Many2many(
        comodel_name='hr.payslip',
        string='Nómina',
        required=True
    )
    txt_filename = fields.Char(string='Nombre Archivo generado')
    txt_binary = fields.Binary(string='Archivo')
    txt_filename2 = fields.Char(string='Nombre Archivo generado 2')
    txt_binary2 = fields.Binary(string='Archivo 2')

    def name_get(self):
        return [(obj.id, '{}'.format(obj.payment_date.strftime('%d/%m/%Y') or '')) for obj in self]

    def generate_files(self):
        parent_bank_id = self.payment_type_id.bank_id
        str_bank = ' - '
        data = {'row1': [], 'row2': [], 'extra_file': False}
        if parent_bank_id and parent_bank_id.bic == '02':
            code = '02'
            str_bank = ' BCP '
            data = self.generate_bcp_file(data)
        elif parent_bank_id and parent_bank_id.bic == '03':
            code = '03'
            data = self.generate_interbank_file(data)
            str_bank = ' Interbank '
        elif parent_bank_id and parent_bank_id.bic == '09':
            code = '09'
            data = self.generate_scotiabank_file(data)
            data['extra_file'] = True
            str_bank = ' Scotia '
        elif parent_bank_id and parent_bank_id.bic == '11':
            code = '11'
            data = self.generate_bbva_file(data)
            data['extra_file'] = False
            str_bank = ' BBVA '
        else:
            code = 'EE'

        str_file = 'Reporte Banco ' + str(str_bank)
        report_bank = BankReportTxt(str_file, code, data)
        txt_1 = report_bank.get_content()
        values = {
            'txt_filename': report_bank.get_filename(),
            'txt_binary': txt_1 or base64.b64encode(b'\n')
        }
        if data['extra_file']:
            report_bank_2 = BankReportTxt('Reporte Banco 2', '', data)
            txt_2 = report_bank_2.get_content()
            values.update({
                'txt_filename2': report_bank_2.get_filename(),
                'txt_binary2': txt_2 or base64.b64encode(b'\n')
            })
        self.write(values)

    def get_data_bbva_wage(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')
        company_bank_id = self.payment_type_id.bank_id.id if self.payment_type_id.acc_number else ''
        if not company_bank_id:
            raise ValidationError('El campo Código de la cuenta de la compañia no puede estar vacía')

        employees_no_accounts = []
        total_amount = 0
        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            row2_val1 = '002'
            row2_val2 = 'L'
            if employee.type_identification_id.code == '7':
                row2_val2 = 'P'
            if employee.type_identification_id.code == '4':
                row2_val2 = 'P'

            row2_val3 = employee.identification_id if employee.identification_id else ''
            row2_val3 = row2_val3.ljust(12)
            row2_val4 = 'P'
            if not employee.bank_account_id:
                row2_val5 = ''
                employees_no_accounts.append('  - ' + employee.name)
            else:
                row2_val5 = employee.bank_account_id.acc_number
                if employee.bank_account_id.bank_id.id != company_bank_id:
                    row2_val4 = 'I'
                    row2_val5 = employee.bank_account_id.cci
            if not row2_val5:
                row2_val5 = ''
            row2_val5 = row2_val5.rjust(20)
            row2_val6 = self.complete_str_data('{} {} {}'.format(employee.firstname or '', employee.lastname or '', employee.secondname or ''), 40, 'right')
            row2_val7 = 0
            for payslip in employee_payslips:
                row2_val7 += sum(round(line.total, 2) for line in payslip.line_ids.filtered(lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
            total_amount += row2_val7
            row2_val7 = self.struct_zero_number(row2_val7, 13).replace('.', '')
            row2_val8 = self.complete_str_data('Referencia Beneficiario {}'.format(employee.identification_id), 40,
                                               'right')
            row2_val9 = ''
            row2_val10 = '00'
            row2_val11 = ''  #  '0' * 30
            row2_val12 = ''  # '0' * 18

            row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + \
                   row2_val9 + row2_val10 + row2_val11 + row2_val12

            data_lines.append(row2)

        if employees_no_accounts:
            error = 'Los siguientes trabajadores no tienen número de cuenta en el campo bank_account_id:\n%s'
            raise ValidationError(error % '\n'.join(employees_no_accounts))
        data['row2'] = data_lines

        # row 1
        payment_date = self.payment_date.strftime('%Y%m%d')
        row1_val1 = '700'
        row1_val2 = str(self.payment_type_id.acc_number)
        row1_val2 = row1_val2.rjust(20)
        row1_val3 = 'PEN' if not self.payment_type_id.currency_id else self.payment_type_id.currency_id.name
        row1_val4 = self.struct_zero_number(total_amount, 13).replace('.', '')
        row1_val5 = 'F'
        row1_val6 = payment_date
        row1_val7 = ' '
        row1_val8 = str('Pago nomina ' + payment_date).ljust(25)
        row1_val9 = self.struct_zero_number_only(len(data_lines), 6)
        # str().rjust(6) # completar con 0
        row1_val10 = 'S' if self.is_validate_account == True else 'N'

        row1_val11 = '0' * 15
        row1_val12 = '0' * 3
        row1_val13 = ''  # '0' * 30
        row1_val14 = ''  # '0' * 20
        data['row1'] = row1_val1 + row1_val2 + row1_val3 + row1_val4 + row1_val5 + row1_val6 + row1_val7 + row1_val8 \
                       + row1_val9 + row1_val10 + row1_val11 + row1_val12 + row1_val13 + row1_val14

        return data

    def get_data_scotiabank_wage(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')

        employees_no_accounts = []
        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            row2_val1 = '21' if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD' else '20'
            row2_val1 = row2_val1.zfill(13)
            row2_val2 = ' ' * 20
            row2_val3 = self.complete_str_data('{} {} {}'.format(employee.firstname or '', employee.lastname or '', employee.secondname or ''), 30, 'right')
            row2_val4 = '1'
            row2_val5 = ' ' * 8
            row2_val6 = 0
            for payslip in employee_payslips:
                row2_val6 += sum(line.total for line in payslip.line_ids.filtered(lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
            if row2_val1 == '21':
                row2_val6 /= self.exchange_type
            row2_val6 = '0.' + self.struct_zero_number_scotia(row2_val6, 11, 9)
            row2_val7 = '.000000000.000000000.000000000.000000000.00'

            scotia_bank_account_id = self.get_partner_bank_by_code(employee, '09', '=', self.acc_type)
            other_bank_account_id = self.get_partner_bank_by_code(employee, '09', '!=', self.acc_type)

            if len(scotia_bank_account_id) == 1 and scotia_bank_account_id.acc_number:
                row2_val8 = self.complete_str_data(scotia_bank_account_id.acc_number, 30, 'right')
            else:
                row2_val8 = ' ' * 30
                scotia_bank_account_id = False

            if len(other_bank_account_id) == 1 and other_bank_account_id.cci:
                row2_val14 = self.complete_str_data(other_bank_account_id.cci, 20, 'right')
            else:
                row2_val14 = ' ' * 30
                other_bank_account_id = False

            if scotia_bank_account_id and other_bank_account_id or not scotia_bank_account_id and not other_bank_account_id:
                employees_no_accounts.append('  - ' + employee.name)
                continue

            row2_val9 = '5'
            row2_val10 = ' ' * 14

            type_identification_id = employee.type_identification_id
            if type_identification_id and type_identification_id.code == '1':
                row2_val11 = '01'
            elif type_identification_id and type_identification_id.code == '4':
                row2_val11 = '02'
            elif type_identification_id and type_identification_id.code == '7':
                row2_val11 = '07'
            else:
                row2_val11 = 'EE'
            row2_val12 = self.complete_str_data(employee.identification_id, 12, 'right')

            row2_val13 = ' ' * 38

            row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + row2_val9 + row2_val10 + row2_val11 + \
                   row2_val12 + row2_val13 + row2_val14
            data_lines.append(row2)

        if employees_no_accounts:
            error = 'Los siguientes trabajadores no tienen número de cuenta en el campo bank_account_id:\n%s'
            raise ValidationError(error % '\n'.join(employees_no_accounts))
        data['row2'] = data_lines
        return data


    def get_data_scotiabank_cts(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')
        row1_val4 = 0
        if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD':
            row2_val2 = '01'
        elif self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'PEN' or not self.payment_type_id.currency_id:
            row2_val2 = '92'
        else:
            row2_val2 = '00'

        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            # row 2
            row2_val1 = '1'
            bank_account_id = self.get_partner_bank_by_code(employee, '09', '=', self.acc_type)
            if len(bank_account_id) == 1 and bank_account_id.acc_number:
                row2_val3 = bank_account_id.acc_number
            else:
                continue
            row2_val3 = self.complete_str_data(row2_val3, 10, 'right')
            row2_val4 = row2_val2

            row2_val5 = 0
            row2_val8 = 0
            for payslip in employee_payslips:
                row2_val5 += sum(line.total for line in payslip.line_ids.filtered(
                    lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
                row2_val8 += sum(line.total for line in payslip.line_ids.filtered(lambda x: x.code == 'TRE_001'))

            if row2_val4 == '01':
                row2_val5 /= self.exchange_type
                row2_val8 /= self.exchange_type
            row1_val4 += row2_val5
            row2_val5 = self.struct_zero_number(row2_val5, 13).replace('.', '')
            row2_val8 = self.struct_zero_number(row2_val8, 13).replace('.', '')
            row2_val6 = ' ' * 20
            company_currency = self.env.user.company_id.currency_id
            if company_currency and company_currency.name == 'USD':
                row2_val7 = '01'
            elif company_currency and company_currency.name == 'PEN' or not company_currency.currency_id:
                row2_val7 = '92'
            else:
                row2_val7 = '00'
            row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8
            data_lines.append(row2)

        data['row2'] = data_lines

        # row 1
        row1_val1 = '0NO'
        row1_val2 = ' ' * 10
        row1_val3 = row2_val2
        row1_val4 = self.struct_zero_number(row1_val4, 13).replace('.', '')
        row1_val5 = '0' * 11
        row1 = row1_val1 + row1_val2 + row1_val3 + row1_val4 + row1_val5
        data['row1'] = row1
        return data

    def get_data_scotiabank_wage2(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')

        employees_no_accounts = []
        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            row2_val1 = self.complete_str_data('{}'.format(employee.identification_id), 8, 'left')
            row2_val2 = self.complete_str_data(
                '{} {} {}'.format(employee.firstname or '', employee.lastname or '', employee.secondname or ''), 30,
                'right')

            row2_val3 = self.complete_str_data(
                '{}'.format(employee_payslips.payslip_run_id.name or ''), 20, 'right')
            row2_val4 = str(self.payment_date).replace("-", "")
            row2_val5 = 0.0
            for payslip in employee_payslips:
                row2_val5 += sum(line.total for line in payslip.line_ids.filtered(
                    lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))

            row2_val5 = str(self.struct_zero_number(row2_val5, 11).replace('.', ''))

            scotia_bank_account_id = self.get_partner_bank_by_code(employee, '09', '=', self.acc_type)

            if len(scotia_bank_account_id) == 1 and scotia_bank_account_id.acc_number:
                row2_val6 = self.complete_str_data(scotia_bank_account_id.acc_number, 11, 'right')
            else:
                row2_val6 = ' ' * 11

            row2_val7 = self.complete_str_data('{}'.format(employee.identification_id), 8, 'left')
            row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7
            data_lines.append(row2)

        if employees_no_accounts:
            error = 'Los siguientes trabajadores no tienen número de cuenta en el campo bank_account_id:\n%s'
            raise ValidationError(error % '\n'.join(employees_no_accounts))
        data['row2'] = data_lines
        return data

    def get_data_scotiabank_cts2(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')

        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            row2_val1 = self.complete_str_data('{}'.format(employee.identification_id), 8, 'left')
            row2_val2 = self.complete_str_data(
                '{} {} {}'.format(employee.firstname or '', employee.lastname or '', employee.secondname or ''), 30,
                'right')

            row2_val3 = self.complete_str_data(
                '{}'.format(employee_payslips.payslip_run_id.name or ''), 20, 'right')
            row2_val4 = str(self.payment_date).replace("-", "")
            row2_val5 = 0.0

            for payslip in employee_payslips:
                row2_val5 += sum(line.total for line in payslip.line_ids.filtered(
                    lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
                # row2_val8 += sum(line.total for line in payslip.line_ids.filtered(lambda x: x.code == 'TRE_001'))

            row2_val5 = str(self.struct_zero_number(row2_val5, 11).replace('.', ''))
            scotia_bank_account_id = self.get_partner_bank_by_code(employee, '09', '=', self.acc_type)

            if len(scotia_bank_account_id) == 1 and scotia_bank_account_id.acc_number:
                row2_val6 = self.complete_str_data(scotia_bank_account_id.acc_number, 11, 'right')
            else:
                row2_val6 = ' ' * 11

            row2_val7 = self.complete_str_data('{}'.format(employee.identification_id), 8, 'left')
            row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7
            data_lines.append(row2)

        data['row2'] = data_lines

        return data

    def generate_scotiabank_file(self, data):
        if self.acc_type == 'wage':
            data = self.get_data_scotiabank_wage(data)
            data = self.get_data_scotiabank_wage2(data)
        elif self.acc_type == 'cts':
            data = self.get_data_scotiabank_cts(data)
            data = self.get_data_scotiabank_cts2(data)
        return data

    def generate_bbva_file(self, data):
        if self.acc_type == 'wage':
            data = self.get_data_bbva_wage(data)
        #elif self.acc_type == 'cts':
        #    data = self.get_data_bbva_cts(data)
        return data

    def generate_bcp_file(self, data):
        employee_accounts = []
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')
        company_account = self.payment_type_id.acc_number
        if not self.payment_type_id.type_bank_code:
            raise ValidationError('El campo Código de la cuenta de la compañia no puede estar vacía')

        row1_val8 = 0
        employees_no_accounts = []
        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            # row 2

            if self.is_validate_account:
                bank_account_id = self.get_partner_bank_by_code(employee, '02', '=', self.acc_type)
                row2_val2 = self.complete_str_data(
                    bank_account_id.acc_number, 20, 'right') if len(
                    bank_account_id) == 1 and bank_account_id.acc_number else False
                row2_val11 = 'S'
                row2_val1 = '2A'
                if not row2_val2:
                    row2_val2 = employee.bank_account_id.cci
                    row2_val11 = 'N'
                    row2_val1 = '2B'
            else:
                bank_account_id = self.get_partner_bank_by_code(employee, False, '!=', self.acc_type)
                row2_val2 = False
                row2_val11 = False
                if bank_account_id:
                    code_02 = bank_account_id.filtered(lambda x: x.bank_id.bic == '02')
                    if code_02:
                        row2_val2 = self.complete_str_data(
                            code_02.acc_number, 20, 'right') if len(code_02) == 1 and code_02.acc_number else False
                        row2_val11 = 'S'
                        bank_account_id = code_02
                        row2_val1 = '2A'
                    else:
                        row2_val2 = self.complete_str_data(
                            bank_account_id.cci, 20, 'right') if len(
                            bank_account_id) == 1 and bank_account_id.cci else False
                        row2_val11 = 'N'
                        row2_val1 = '2B'
                else:
                    row2_val1 = ''
            if self.acc_type == 'cts' and bank_account_id.bank_id.bic != '02':
                continue
            if not row2_val2:
                employees_no_accounts.append('  - ' + employee.name)
                continue

            row2_val3 = 'E'
            type_identification_id = employee.type_identification_id
            if type_identification_id:
                if type_identification_id.code == '1':
                    row2_val3 = '1'
                elif type_identification_id.code == '4':
                    row2_val3 = '3'
                elif type_identification_id.code == '7':
                    row2_val3 = '4'
            row2_val4 = self.complete_str_data(employee.identification_id, 15, 'right')
            row2_val5 = self.complete_str_data(
                '{} {} {}'.format(employee.firstname or '', employee.lastname or '', employee.secondname or ''), 75,
                'right')
            row2_val6 = self.complete_str_data('Referencia Beneficiario {}'.format(employee.identification_id), 40,
                                               'right')
            val7 = 'Ref Emp {}'.format(employee.identification_id)
            row2_val7 = self.complete_str_data(val7, 20, 'right')
            row2_val8 = '1' if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD' else '0'
            row2_val9 = '001'
            row2_val10 = 0
            row2_val13 = 0
            for payslip in employee_payslips:
                row2_val10 += sum(line.total for line in payslip.line_ids.filtered(
                    lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
                if self.acc_type == 'cts':
                    row2_val13 += sum(line.total for line in payslip.line_ids.filtered(lambda x: x.code == 'TRE_001'))
            row1_val8 += row2_val10
            if row2_val8 == '1':
                row2_val10 /= self.exchange_type
            row2_val10 = self.struct_zero_number(row2_val10, 14)
            if self.acc_type == 'wage':
                row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + \
                       row2_val9 + row2_val10 + row2_val11
                employee_accounts.append((row2_val2, row2_val1[1:]))
            else:
                row2_val12 = '001'
                if row2_val8 == '1':
                    row2_val13 /= self.exchange_type
                row2_val11 = '1' if self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.name == 'USD' else '0'
                row2_val13 = self.struct_zero_number(row2_val13, 14)
                row2 = row2_val1[0] + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + row2_val9 + row2_val10 + row2_val11 \
                       + row2_val12 + row2_val13
                employee_accounts.append((row2_val2, 'A'))
            data_lines.append(row2)

        if employees_no_accounts:
            error = 'Los siguientes trabajadores no tienen número de cuenta en el campo bank_account_id:\n%s'
            raise ValidationError(error % '\n'.join(employees_no_accounts))

        data['row2'] = data_lines
        payment_date = self.payment_date.strftime('%Y%m%d')

        # row 1
        row1_val1 = str(len(data_lines))[:6].zfill(6)
        row1_val2 = payment_date
        row1_val3 = 'X'
        row1_val4 = self.payment_type_id.type_bank_code
        row1_val5 = '1' if self.payment_type_id and self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD' else '0'
        row1_val6 = '001'
        row1_val7 = company_account.replace('-', '').ljust(20, ' ') if company_account else ' ' * 20

        acc_type = dict(type_payment).get(self.acc_type).upper()
        row1_val9 = self.complete_str_data(acc_type, 40, 'right')
        row1_val10 = self.get_identifier(employee_accounts, company_account)
        if row1_val5 == '1':
            row1_val8 /= self.exchange_type
        row1_val8 = self.struct_zero_number(row1_val8, 14)
        if self.acc_type == 'wage':
            row1 = row1_val1 + row1_val2 + row1_val3 + row1_val4 + row1_val5 + row1_val6 + row1_val7 + row1_val8 + \
                   row1_val9 + row1_val10
        else:
            company_vat = self.complete_str_data(self.env.user.company_id.partner_id.vat, 12, 'right')
            row1_val9 = self.complete_str_data('Referencia {}'.format(acc_type), 40, 'right')
            row1 = row1_val1 + row1_val2 + row1_val4 + row1_val5 + row1_val6 + row1_val7 + '6' + company_vat + row1_val8 + row1_val9 + row1_val10
        data['row1'] = '1' + row1
        return data

    def generate_interbank_file(self, data):
        data_lines = []
        employees_ids = self.payslip_ids.mapped('employee_id')
        i = 1
        net = 0

        employees_no_accounts = []
        row2_val2 = ''
        for employee in employees_ids:
            employee_payslips = self.payslip_ids.filtered(lambda x: x.employee_id == employee)
            # row 2
            row2_val1 = '02'
            if employee.type_identification_id.l10n_pe_vat_code == '1':
                row2_val2 = '01' + str(employee.identification_id)

            elif employee.type_identification_id.l10n_pe_vat_code == '4':
                row2_val2 = '03' + str(employee.identification_id)

            elif employee.type_identification_id.l10n_pe_vat_code == '7':
                row2_val2 = '05' + str(employee.identification_id)
            else:
                row2_val2 = ''

            row2_val2 = self.complete_str_data(row2_val2.zfill(10), 49, 'right')

            # row2_val2 = self.complete_str_data(str(i).zfill(2), 49, 'right')

            if self.is_validate_account:
                bank_account_id = self.get_partner_bank_by_code(employee, '03', '=', self.acc_type)
                row2_val9 = self.complete_str_data(
                    bank_account_id.acc_number, 23, 'right') if len(
                    bank_account_id) == 1 and bank_account_id.acc_number else False
            else:
                bank_account_id = self.get_partner_bank_by_code(employee, False, '!=', self.acc_type)
                row2_val9 = False
                if bank_account_id:
                    code_03 = bank_account_id.filtered(lambda x: x.bank_id.bic == '03')
                    if code_03:
                        row2_val9 = self.complete_str_data(
                            code_03.acc_number, 23, 'right') if len(code_03) == 1 and code_03.acc_number else False
                        bank_account_id = code_03
                    else:
                        row2_val9 = self.complete_str_data(
                            bank_account_id.cci, 23, 'right') if len(
                            bank_account_id) == 1 and bank_account_id.cci else False

            if not row2_val9:
                employees_no_accounts.append('  - ' + employee.name)
                continue

            row2_val3 = '10' if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD' else '01'
            row2_val4 = 0.00
            row2_val15 = 0
            for payslip in employee_payslips:
                row2_val4 += sum(line.total for line in payslip.line_ids.filtered(
                    lambda x: x.category_id == self.env.ref('hr_payroll.NET', False)))
                if self.acc_type == 'cts':
                    row2_val15 += sum(line.total for line in payslip.line_ids.filtered(lambda x: x.code == 'TRE_001'))
                net += row2_val4
            if row2_val3 == '10':
                row2_val4 /= self.exchange_type
            row2_val4 = self.struct_zero_number(row2_val4, 16)
            row2_val4 = row2_val4[3:].replace('.', '')
            row2_val5 = ' '

            if self.payment_type_id.bank_id.bic == bank_account_id.bank_id.bic and bank_account_id.acc_type == \
                    self.acc_type:
                row2_val6 = '09'
                row2_val7 = '002'
            else:
                row2_val6 = '99'
                row2_val7 = '   '

            row2_val8 = '10' if bank_account_id.currency_id and bank_account_id.currency_id.name == 'USD' else '01'
            row2_val10 = 'P'
            row2_val11 = row2_val8
            row2_val12 = self.complete_str_data(employee.identification_id, 15, 'right')
            firstname = self.complete_str_data(employee.firstname, 20, 'right')
            lastname = self.complete_str_data(employee.lastname, 20, 'right')
            secondname = self.complete_str_data(employee.secondname, 20, 'right')
            row2_val13 = '{}{}{}'.format(firstname, lastname, secondname)
            if self.acc_type == 'wage':
                row2_val14 = '0' * 15
                row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + row2_val9 + row2_val10 + row2_val11 + \
                       row2_val12 + row2_val13 + row2_val14
            else:
                row2_val14 = '10' if self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.name == 'USD' else '01'
                row2_val15 = self.struct_zero_number(row2_val15, 16)
                row2_val15 = row2_val15[3:].replace('.', '')
                if self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.name == 'USD':
                    row2_val15 /= self.exchange_type
                row2 = row2_val1 + row2_val2 + row2_val3 + row2_val4 + row2_val5 + row2_val6 + row2_val7 + row2_val8 + row2_val9 + row2_val10 + row2_val11 + \
                       row2_val12 + row2_val13 + row2_val14 + str(row2_val15)
            data_lines.append(row2)

        if employees_no_accounts:
            error = 'Los siguientes trabajadores no tienen número de cuenta en el campo bank_account_id:\n%s'
            raise ValidationError(error % '\n'.join(employees_no_accounts))
        data['row2'] = data_lines
        # row 1
        now = self.convert_date_timezone(datetime.now())
        row1_val1 = self.complete_str_data('0104', 40, 'right') if self.acc_type != 'cts' else self.complete_str_data(
            '0106', 40, 'right')
        row1_val2 = self.payment_date.strftime('%Y%m%d')
        row1_val3 = self.complete_str_data(now.strftime("%H%M%S"), 15, 'right')
        row1_val4 = str(len(data_lines))[:6].zfill(6)
        if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD':
            net /= self.exchange_type
        net = self.struct_zero_number(net, 16)
        net = net[3:].replace('.', '')
        row1_val5 = net if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'PEN' \
            else '0' * 15
        row1_val6 = net if self.payment_type_id.currency_id and self.payment_type_id.currency_id.name == 'USD' \
            else '0' * 15
        row1_val7 = 'MC001'
        if self.acc_type == 'wage':
            row1 = row1_val1 + row1_val2 + row1_val3 + row1_val4 + row1_val5 + row1_val6 + row1_val7
        else:
            row1 = row1_val1 + row1_val2 + row1_val3 + row1_val4 + row1_val5 + row1_val6 + row1_val7
        data['row1'] = row1
        return data

    def get_identifier(self, employee_accounts, company_account):
        total_abonos = 0
        total_cargo = self.get_clean_account(company_account, 'A')
        for account, type_account in employee_accounts:
            total_abonos += self.get_clean_account(account, type_account)
        total_control = total_cargo + total_abonos
        return str(total_control).zfill(15)

    @staticmethod
    def get_clean_account(account, type_account):
        try:
            account = account.replace(' ', '')
            account = account.replace('-', '')
            if type_account == 'B':
                return int(account[10:len(account)])
            else:
                return int(account[3:len(account)])
        except:
            return 0

    def get_partner_bank_by_code(self, employee, code, operator, acc_type):
        partner_bank_model = self.env['res.partner.bank']
        domain = [
            ('partner_id', '=', employee.address_home_id.id),
            ('bank_id', '!=', False),
            ('bank_id.bic', operator, code),
            ('acc_type', '=', acc_type),
            ('currency_id', '!=', False)
        ]
        bank_account_id = partner_bank_model.search(domain)
        return bank_account_id

    @staticmethod
    def struct_zero_number(value, digits):
        struct = '%{}.2f'.format(digits)
        value = float(struct % value)
        decimal = ('%.2f' % (value - int(value)))[1:]
        integer = str(int(value)).zfill(digits)
        value = integer + decimal
        return value

    @staticmethod
    def struct_zero_number_only(value, digits):
        struct = '%{}.2f'.format(digits)
        value = float(struct % value)
        integer = str(int(value)).zfill(digits)
        value = integer
        return value

    @staticmethod
    def struct_zero_number_scotia(value, int_digits, decimal_digits):
        struct = '%{}.2f'.format(int_digits)
        value = float(struct % value)
        decimal = ('%.2f' % (value - int(value)))[2:]
        integer = str(int(value)).zfill(int_digits)
        decimal = decimal.ljust(decimal_digits, '0')
        value = '{}.{}'.format(integer, decimal)
        return value

    @staticmethod
    def complete_str_data(data, length, position):
        if data:
            if position == 'left':
                value = data[0:length].rjust(length, ' ')
            else:
                value = data[0:length].ljust(length, ' ')
        else:
            value = ' ' * length
        return value

    def convert_date_timezone(self, date_order, format_time='%Y-%m-%d %H:%M:%S'):
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        if isinstance(date_order, str):
            date_order = datetime.strptime(date_order, format_time)
        if date_order:
            date_tz = pytz.utc.localize(date_order).astimezone(tz)
            date_order = date_tz.strftime(format_time)
            date_order = datetime.strptime(date_order, format_time)
        return date_order
