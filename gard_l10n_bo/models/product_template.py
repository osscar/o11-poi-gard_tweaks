# -*- coding: utf-8 -*-

# import logging

from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError

# _logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    siat_unidad_medida_id = fields.Many2one(
        "siat.unidad_medida",
        string="UdM SIAT",
        compute="_get_siat_unidad_medida",
        store="True",
        help="La Unidad de medida SIAT por defecto con el que se enviará la venta de este Producto al SIN.",
    )

    @api.multi
    @api.depends("uom_id", "uom_id.siat_unidad_medida_id")
    def _get_siat_unidad_medida(self):
        siat_uom_id = False
        for product in self:
            if product.uom_id and product.uom_id.siat_unidad_medida_id:
                siat_uom_id = product.uom_id.siat_unidad_medida_id
            product.siat_unidad_medida_id = siat_uom_id
        return True
