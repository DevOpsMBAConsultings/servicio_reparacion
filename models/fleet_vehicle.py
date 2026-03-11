# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    customer_id = fields.Many2one('res.partner', string='Cliente')
    engine_hours = fields.Float(
        string='Horas de Motor',
        compute='_compute_engine_hours',
        inverse='_set_engine_hours',
        help='Últimas horas registradas del motor',
        store=False,
    )

    def _compute_engine_hours(self):
        for record in self:
            record.engine_hours = 0.0
            last_log = self.env['fleet.vehicle.engine_hour'].search([
                ('vehicle_id', '=', record.id)
            ], limit=1, order='date desc, id desc')
            if last_log:
                record.engine_hours = last_log.value

    def _set_engine_hours(self):
        for record in self:
            if record.engine_hours:
                self.env['fleet.vehicle.engine_hour'].create({
                    'value': record.engine_hours,
                    'date': fields.Date.context_today(record),
                    'vehicle_id': record.id
                })

class FleetVehicleEngineHour(models.Model):
    _name = 'fleet.vehicle.engine_hour'
    _description = 'Engine Hour Log'
    _order = 'date desc, id desc'

    name = fields.Char(compute='_compute_name', store=True)
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float('Engine Hours', required=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, ondelete='cascade')

    @api.depends('vehicle_id', 'date')
    def _compute_name(self):
        for record in self:
            name = record.vehicle_id.name
            if not name:
                name = _("New Engine Hour Log")
            record.name = f"{name} / {record.date}"
