# -*- coding: utf-8 -*-
##############################################################################
#
#    Bli Bli, Ltd.
#    Copyleft and swindle theft.
#    Author: squid
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api


class ProductProduct(models.Model):
  _inherit = 'product.product'

  @api.multi
  def button_product_stock_quantity(self):
    product_id = self.id
    view_id = self.env.ref(
        'gard_product_stock_qty.product_stock_quantity_view_tree').id

    return {
        'type': 'ir.actions.act_window',
        'name': 'Product Stock Quantity',
        'res_model': 'stock.quant',
        'domain': [('product_id', '=', product_id),
                   ('location_id.usage', '=', 'internal')],
        # 'view_type': 'tree',
        'view_mode': 'tree',
        # 'views': [(view_id, 'tree')],
        'view_id': view_id,
        'context': {'group_by': ['location_id', 'product_id']},
        'target': 'new',
    }

  location_ids = fields.One2many('stock.quant',
                                 'product_id',
                                 domain=[
                                     ('location_id.usage', '=', 'internal')],
                                 store=True,
                                 string="Product Stock Quantity")


class ProductTemplate(models.Model):
  _inherit = 'product.template'

  location_ids = fields.One2many('stock.quant',
                                 'product_id',
                                 domain=[
                                     ('location_id.usage', '=', 'internal')],
                                 store=True,
                                 string="Product Stock Quantity")
