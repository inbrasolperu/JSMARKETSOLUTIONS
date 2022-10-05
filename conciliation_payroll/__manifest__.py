# -*- coding: utf-8 -*-
{
    'name': 'Conciliation payroll',
    'version': '13.0.1.2.0',
    'author': 'Yaroslab/Ganemo',
    'website': 'http://www.yaroslab.com',
    'description': "",
    'depends': [
        'hr_payroll_account',
        'txt_bank_lo_pe',
    ],
    'data': [
        'views/hr_massive_payment_views.xml',
        'views/hr_payslip_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
