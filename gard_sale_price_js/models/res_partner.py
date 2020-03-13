# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pricelist_ids = fields.Many2many(
        'product.pricelist',
        # 'product_pricelist_partners_rel',
        # 'pricelist_id', 'partner_id',
        domain=[('active', '=', True)],
        string='Pricelists')
