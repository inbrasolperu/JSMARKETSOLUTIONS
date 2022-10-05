# -*- coding: utf-8 -*-
{
    'name': 'Tolerance tardiness',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Crea en attendance una columna donde se calcula la tardanza del trabajador.
    """,
    'depends': ['hr_attendance'],
    'data': [
        'views/hr_views.xml',
        'views/resource_calendar_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
