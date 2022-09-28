# -*- coding: utf-8 -*-
{
    'name': 'Employee Service from Contracts',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
    Este modulo complementa el modulo de employee_service ya que realiza la conexión con los contratos de trabajo .
    """,
    'depends': [
        'employee_service',
        'hr_contract'
    ],
    'data': [
        'views/crons.xml',
        'views/hr_employee_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
