# -*- coding: utf-8 -*-
{
    'name': 'HR - loan advance other',
    'version': '13.0.1.0',
    'author': 'Yaroslab/Ganemo',
    'website': 'http://www.yaroslab.com',
    'description': """""",
    'category': 'Generic Modules/Human Resources',
    'depends': [
        'account',
        'hr_payroll',
        'automatic_functions_rule'
    ],
    'data': [
        'data/hr_data.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_loan_views.xml',
        'views/hr_other_discounts_views.xml',
        'views/hr_salary_advance_views.xml',
        'views/hr_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
