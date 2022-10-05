# -*- coding: utf-8 -*-
{
    'name': 'Contract formats',
    'version': '13.0.1.0.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
    """,
    'depends': [
        'additional_fields_voucher',
        'identification_type_employee'
    ],
    'data': [
        'data/template_contract.xml',
        'views/crons.xml',
        'views/email_template_views.xml',
        'views/hr_contract_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
