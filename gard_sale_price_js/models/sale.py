# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields, api, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def get_pricelist_items(self):
        """ Open xml view specified in xml_id for current product """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id(
                'gard_sale_price', xml_id)
            res.update(
                domain=[('product_id', '=',
                         # self.product_id.product_tmpl_id.id),
                         self.product_id.id),
                        ('active_pricelist', '=', True)]
                        # '|',
                        # ('date_end', '=', []),
                        # ('date_end', '>=',
                        #  datetime.datetime.now().strftime('%Y-%m-%d'))]
            )
            return res
        return False
