# -*- coding: utf-8 -*-

# import logging

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError

# _logger = logging.getLogger(__name__)


class ProductUoM(models.Model):
    _inherit = "product.uom"

    siat_unidad_medida_id = fields.Many2one(
        "siat.unidad_medida",
        string="UdM SIAT",
        help="La Unidad de medida SIAT con el que se enviará la venta de este Producto al SIN.",
    )
