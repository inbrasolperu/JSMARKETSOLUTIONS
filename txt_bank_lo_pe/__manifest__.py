# -*- coding: utf-8 -*-
{
    'name': 'TXT sueldo y cts BCP, Interbank, Scotia y BBVA',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
    Genera los archivos de texto de sueldos y cts para los bancos BCP, Interbank, Scotia y BBVA.
    """,
    'depends': [
        'hr_localization_menu',
        'hr_payroll',
        'type_bank_accounts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_massive_payment_views.xml',
        'views/res_partner_bank_views.xml',
        'views/hr_payslip_net_others.xml',
    ],
    'installable': True,
    'auto_install': False,
}
