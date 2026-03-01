# -*- coding: utf-8 -*-
from odoo import models, fields

class Mecanico(models.Model):
    """Técnico/Mecánico que trabaja en las órdenes de reparación."""
    _inherit = 'hr.employee'

    is_mecanico = fields.Boolean(
        string='Es Mecánico',
        help='Indica que este empleado es un técnico del servicio de reparación.'
    )
