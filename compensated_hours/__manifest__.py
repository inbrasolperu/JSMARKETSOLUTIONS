# -*- coding: utf-8 -*-
{
    'name': 'Compensated hours',
    'version': '13.0.1.0.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Este módulo registra automático las asignación de horas compensadas las cuales se migran del módulo extra_hours, si el usuario indica que son horas compensadas. 
    """,
    'depends': [
        'extra_hours',
        'automatic_leave_type'
    ],
    'installable': True,
    'auto_install': False,
}
