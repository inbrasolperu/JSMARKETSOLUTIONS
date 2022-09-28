# coding: utf-8


from odoo import api, fields, models, exceptions, _

class WizardGeneratedTags(models.TransientModel):
    _name = 'hr.timesheet.tag.generated'

    date_begin = fields.Date(
        string='Fecha Inicio'
    )
    date_end = fields.Date(
        string='Fecha Inicio'
    )
    company_id = fields.Many2one(
        'res.company',
        string="Compañia",
        # default=self.env.user.company_id.id
    )

    # @api.one
    def generated_report(self):
        if self.date_end < self.date_begin:
            raise exceptions.ValidationError(
                _('La fecha de inicio no puede ser mayor a la fecha final')
            )
        self.env['account.analytic.line'].get_timesheet_for_project_mounth(
            self.date_begin,
            self.date_end,
            self.company_id.id
        )
