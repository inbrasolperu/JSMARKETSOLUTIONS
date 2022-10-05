# -*- coding: utf-8 -*-
{
    "name": u"Automatic leave type",
    'version': '13.0.1.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    "description": """
Este módulo importa los tipos de ausencias que existen en la Planilla Electronica del Perú.
    """,
    "depends": [
        'hr_payroll',
        'project_timesheet_holidays'
    ],
    "data": [
        'data/hr_work_entry_type_data.xml',
        'data/hr_leave_type_data.xml',
        'views/hr_views.xml'
    ],
    "installable": True,
    "active": False,
}
