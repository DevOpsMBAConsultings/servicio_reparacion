# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_servicio_cliente = fields.Boolean(
        string='Es Cliente de Reparación',
        help='Indica si este contacto es un cliente del servicio de reparación de camiones.'
    )

    vehicle_count = fields.Integer(
        string='Flota',
        compute='_compute_vehicle_count',
    )

    repair_order_count = fields.Integer(
        string='Órdenes de Reparación',
        compute='_compute_repair_order_count',
    )

    @api.depends('is_servicio_cliente')
    def _compute_vehicle_count(self):
        Vehicle = self.env['fleet.vehicle']
        for partner in self:
            partner.vehicle_count = Vehicle.search_count([('customer_id', '=', partner.id)])

    @api.depends('is_servicio_cliente')
    def _compute_repair_order_count(self):
        RepairOrder = self.env['repair.order']
        for partner in self:
            partner.repair_order_count = RepairOrder.search_count([('partner_id', '=', partner.id)])

    def action_view_fleet(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Flota de %s' % self.name,
            'res_model': 'fleet.vehicle',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }

    def action_view_repair_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Reparación de %s' % self.name,
            'res_model': 'repair.order',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
