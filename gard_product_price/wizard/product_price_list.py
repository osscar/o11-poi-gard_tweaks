# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class product_price_list(models.TransientModel):
    _name = 'gard_product_price.price_list'
    _description = 'Price List'

    price_list = fields.Many2one('product.pricelist', 'PriceList', required=True)

    @api.multi
    def print_report(self):
        """
        To get the date and print the report
        @return : return report
        """

        datas = {'ids': self.env.context.get('active_ids', [])}
        res = self.read(['price_list'])
        res = res and res[0] or {}
        res['price_list'] = res['price_list'][0]
        datas['form'] = res
        return self.env.ref('gard_product_price.action_report_pricelist').report_action([], data=datas)
