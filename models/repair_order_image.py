# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RepairOrderImage(models.Model):
    _name = 'repair.order.image'
    _description = 'Imagen de Orden de Reparación'
    _order = 'sequence, id'

    repair_order_id = fields.Many2one(
        'repair.order',
        string='Orden de Reparación',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    image = fields.Binary(string='Imagen', attachment=True)
    description = fields.Char(string='Descripción', placeholder='Descripción de la imagen...')

    @api.constrains('repair_order_id')
    def _check_max_images(self):
        for rec in self:
            if len(rec.repair_order_id.image_ids) > 15:
                raise ValidationError(
                    'Se permite un máximo de 15 imágenes por orden de reparación.'
                )
