# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RepairReportWizard(models.TransientModel):
    _name = 'repair.report.wizard'
    _description = 'Wizard para Informe de Taller'

    repair_id = fields.Many2one('repair.order', string='Orden de Reparación', required=True)
    report_date = fields.Date(string='Fecha del Reporte', default=fields.Date.context_today, required=True)

    def action_print(self):
        self.ensure_one()
        # Pass the date to the report context
        return self.env.ref('servicio_reparacion.action_report_repair_order').with_context(report_date=self.report_date).report_action(self.repair_id)
