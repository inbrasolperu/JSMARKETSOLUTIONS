# -*- coding: utf-8 -*-
{
    'name': 'Payroll tag analytics employee',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
    Este módulo crea variables dentro del empleado ( analytics_tags ), regla salarial(generated_tags_automatic).
    y asigna dentro de cada asiento de concuenta de planilla la(s) distribiion analitica correspondientes
    """,
    'depends': [
        'hr',
        'hr_payroll',
        'payroll_accounting_entry_separate',
        'analytic',
        'hr_payroll_account'
    ],
    'data': [
        'views/hr_views.xml',
        'views/wizard_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
