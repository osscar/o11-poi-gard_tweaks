# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    price_version_ids = fields.Many2many(comodel_name='product.pricelist.version',
                                         relation='product_pricelist_version_partners_rel',
                                         column1='price_version_id',
                                         column2='partner_id',
                                         domain=[('active', '!=', False)],
                                         string='Pricelist Versions')
