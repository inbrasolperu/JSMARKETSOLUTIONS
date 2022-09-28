# -*- coding: utf-8 -*-
{
    'name': 'Autocomplete Name',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Llena de manera automatica el campo name de hr.employee con los campos del modulo personal_information.""",
    'depends': ['personal_information'],
    'data': ['views/hr_views.xml'],
    'installable': True,
    'auto_install': False,
}
