import odoo
from odoo.tools.safe_eval import _BUILTINS
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# from dateutil.rrule import rrule, MONTHLY

# This change permit us to debug hr.salary.rule functions on log file
ADD_BUILTINS = {
    'print': print,
    'exec': exec,

    # local and global variables
    'locals': locals,
    'globals': globals,

    # libraries
    'timedelta': timedelta,
    'relativedelta': relativedelta,
    # 'rrule': rrule,
    # 'MONTHLY': MONTHLY

}
_BUILTINS.update(ADD_BUILTINS)
odoo.tools.safe_eval._BUILTINS = _BUILTINS
