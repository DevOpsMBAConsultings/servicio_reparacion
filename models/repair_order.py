# -*- coding: utf-8 -*-
from odoo import models, fields, api

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    antecedentes_servicio = fields.Text(string='3. Antecedentes del servicio')
    hallazgos = fields.Text(string='4. Hallazgos')
    accion_correctiva = fields.Text(string='5. Acción Correctiva')
    recomendaciones = fields.Text(string='6. Recomendaciones')
    
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo a reparar')

    # Readonly client fields
    partner_email = fields.Char(string='Correo', related='partner_id.email', readonly=True)
    partner_street = fields.Char(string='Dirección', related='partner_id.street', readonly=True)
    partner_phone = fields.Char(string='Teléfono', related='partner_id.phone', readonly=True)

    # Readonly vehicle fields
    vehicle_brand = fields.Char(string='Marca', related='vehicle_id.brand_id.name', readonly=True)
    vehicle_vin = fields.Char(string='Número de Chassis', related='vehicle_id.vin_sn', readonly=True)
    vehicle_plate = fields.Char(string='Placa', related='vehicle_id.license_plate', readonly=True)

    # Added manually by user (vehicle usage) 
    odometer = fields.Float(string='KM (Odómetro)', related='vehicle_id.odometer', readonly=False)
    engine_hours = fields.Float(string='Horas de Motor', related='vehicle_id.engine_hours', readonly=False)
    location = fields.Char(string='Ubicación', related='vehicle_id.location', readonly=False)

    # Images (max 15)
    image_ids = fields.One2many('repair.order.image', 'repair_order_id', string='Imágenes')
    image_count = fields.Integer(compute='_compute_image_count', string='Cantidad de Imágenes')

    # Sale Order integration
    sale_order_ids = fields.One2many('sale.order', 'repair_order_id', string='Cotizaciones')
    sale_order_count = fields.Integer(compute='_compute_sale_order_count', string='Cotizaciones')

    # Technician
    mecanico_id = fields.Many2one(
        'hr.employee',
        string='Técnico Asignado',
        domain=[('is_mecanico', '=', True)],
    )

    # Invoices
    invoice_ids = fields.Many2many(
        'account.move',
        'repair_order_invoice_rel',
        'repair_id', 'invoice_id',
        string='Facturas',
        copy=False,
    )
    invoice_count = fields.Integer(compute='_compute_invoice_count', string='Facturas')

    @api.depends('sale_order_ids')
    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = len(record.sale_order_ids)

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

    @api.depends('image_ids')
    def _compute_image_count(self):
        for record in self:
            record.image_count = len(record.image_ids)

    def action_create_invoice(self):
        self.ensure_one()
        journal = self.env['account.journal'].search([
            ('type', '=', 'sale'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        invoice_lines = []
        for move in self.move_ids.filtered(lambda m: m.repair_line_type == 'add'):
            product = move.product_id
            invoice_lines.append((0, 0, {
                'product_id': product.id,
                'quantity': move.product_uom_qty,
                'product_uom_id': move.product_uom.id,
                'price_unit': product.lst_price,
                'name': product.name,
            }))

        if not invoice_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin elementos',
                    'message': 'Agrega servicios o piezas en la pestaña Piezas antes de generar la factura.',
                    'type': 'warning',
                },
            }

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'journal_id': journal.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_lines,
        })
        self.invoice_ids = [(4, invoice.id)]

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
        }

    def action_view_invoices(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Facturas',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }
        if self.invoice_count == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.invoice_ids.id
        return action

    def action_print_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Imprimir Informe de Taller',
            'res_model': 'repair.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_repair_id': self.id},
        }

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            return {'domain': {'vehicle_id': [('customer_id', '=', self.partner_id.id)]}}
        return {'domain': {'vehicle_id': []}}

    def action_create_quotation(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('servicio_reparacion.action_quotations_servicio_reparacion')
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_repair_order_id': self.id,
            'default_is_servicio_cliente': True,
            'is_servicio_app': True,
        }
        return action

    def action_view_quotations(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('servicio_reparacion.action_quotations_servicio_reparacion')
        action['domain'] = [('repair_order_id', '=', self.id)]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_repair_order_id': self.id,
            'default_is_servicio_cliente': True,
            'is_servicio_app': True,
        }
        if self.sale_order_count == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = self.sale_order_ids.id
        return action

    @api.model
    def get_text_chunks(self, text, max_lines=29):
        """
        Splits text into chunks of max_lines.
        Returns a list of strings.
        """
        if not text:
            return []
        
        # Strip leading/trailing noise to avoid empty chunks or ghost alignment
        text = text.strip()
        if not text:
            return []
            
        lines = text.splitlines()
        chunks = []
        current_chunk = []
        
        for line in lines:
            current_chunk.append(line)
            if len(current_chunk) >= max_lines:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks

    @api.model
    def get_text_lines(self, text):
        """
        Splits text into individual lines and strips them aggressively.
        Handles non-breaking spaces to ensure perfect left alignment in PDFs.
        """
        if not text:
            return []
        # Filter out truly empty lines to prevent vertical gaps between chunks of text
        return [line.strip().replace('\xa0', ' ') for line in text.splitlines() if line.strip()]

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_servicio_cliente = fields.Boolean(string='Es Servicio?', default=False)
    repair_order_id = fields.Many2one('repair.order', string='Orden de Reparación', copy=False)
    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo a Reparar')

    @api.onchange('partner_id')
    def _onchange_partner_id_vehicle_domain(self):
        if self.partner_id:
            return {'domain': {'fleet_vehicle_id': [('customer_id', '=', self.partner_id.id)]}}
        return {'domain': {'fleet_vehicle_id': []}}

    def action_create_repair_order(self):
        self.ensure_one()
        if self.repair_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'repair.order',
                'view_mode': 'form',
                'res_id': self.repair_order_id.id,
            }

        # Create the repair order without mapping the product to product_id
        # (product_id = "item being repaired", not the service being performed)
        repair_vals = {
            'partner_id': self.partner_id.id,
            'vehicle_id': self.fleet_vehicle_id.id if self.fleet_vehicle_id else False,
            'sale_order_ids': [(4, self.id)],
        }

        repair = self.env['repair.order'].create(repair_vals)
        self.repair_order_id = repair.id

        # Add each quotation line as a service/part in the Piezas tab (move_ids)
        for line in self.order_line:
            if not line.product_id:
                continue
            self.env['stock.move'].create({
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_id.uom_id.id,
                'repair_id': repair.id,
                'repair_line_type': 'add',
                'company_id': repair.company_id.id,
                'location_id': repair.location_id.id,
                'location_dest_id': repair.location_dest_id.id,
            })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'form',
            'res_id': repair.id,
        }
