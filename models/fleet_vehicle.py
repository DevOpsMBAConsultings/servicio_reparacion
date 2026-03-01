# -*- coding: utf-8 -*-
from odoo import models, fields

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    customer_id = fields.Many2one('res.partner', string='Cliente')
