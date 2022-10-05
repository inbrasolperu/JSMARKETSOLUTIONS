# -*- coding: utf-8 -*-
{
    'name': 'Career Line',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Este modulo crea una pestaña llamada "Linea de carrera" donde se archiva los movimientos de sueldo y cambios de cargos. 
    """,
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/career_line_views.xml',
        'views/hr_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
