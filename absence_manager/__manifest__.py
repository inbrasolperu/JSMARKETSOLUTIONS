# -*- coding: utf-8 -*-
{
    'name': 'Absence manager',
    'version': '13.0.1.1.0',
    'author': 'Yaroslab',
    'website': 'http://www.yaroslab.com',
    'description': """
Es un modulo dinamico el cual realiza la sincronización entre el modulo de asistencia y el modulo de ausencia, 
realizando una validación con la jornada laboral del trabajador y creando una ausencia automatica para alertar 
cuando exista una falta de asistencia.
    """,
    'depends': [
        'hr_attendance',
        'hr_holidays',
        'absence_day'
    ],
    'data': [
        'views/hr_attendance_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_leave_views.xml',
        'data/hr_leave_type_data.xml',
        'data/ir_cron.xml'
    ],
    'installable': True,
    'auto_install': False,
}
