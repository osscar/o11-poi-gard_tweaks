# -*- coding: utf-8 -*-
# import logging

from itertools import chain
from odoo import models, fields, api, _

import odoo.addons.decimal_precision as dp

from odoo.exceptions import UserError, ValidationError

# _logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners')

    item_product_default_code = fields.Char(
        related='item_ids.product_default_code',
        string="Product Internal Reference",
        help='Product default code.',
        readonly=True)

    is_hidden = fields.Boolean(
        string="Hide items",
        default=False,
        help='Don\'t show items in product price. Helpful when using pricelist solely for calculation purposes on other pricelists.')

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        res = super(ProductPricelist, self)._compute_price_rule(
            products_qty_partner, date=False, uom_id=False)
        
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Date.context_today(self)
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            'SELECT item.id '
            'FROM product_pricelist_item AS item '
            'LEFT JOIN product_category AS categ '
            'ON item.categ_id = categ.id '
            'WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))'
            'AND (item.product_id IS NULL OR item.product_id = any(%s))'
            'AND (item.categ_id IS NULL OR item.categ_id = any(%s)) '
            'AND (item.pricelist_id = %s) '
            'AND (item.date_start IS NULL OR item.date_start<=%s) '
            'AND (item.date_end IS NULL OR item.date_end>=%s)'
            'ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        if self._context.get('item_ids'):
            item_ids = [self._context.get('item_ids', [])]
            items = item_ids
        results = {}
        for product, qty, partner in products_qty_partner:
            # _logger.debug('product >>>: %s', product)
            # _logger.debug('qty >>>: %s', qty)
            # _logger.debug('partner >>>: %s', partner)
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]
            # _logger.debug('cup lst price >>>: %s', price)

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    # bypass min_qty restrict for gard_product_price.product_pricelist_item_tree_view
                    if item_ids:
                        pass
                    else:
                        # _logger.debug('cup rule call not item_ids >>>: %s', item_ids)
                        continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                    # _logger.debug('cup pricelist price_tmp >>>: %s', price_tmp)
                    price = rule.base_pricelist_id.currency_id.compute(price_tmp, self.currency_id, round=False)
                    # _logger.debug('cup pricelist price >>>: %s', price)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]
                    # _logger.debug('cup pricelist else price >>>: %s', price)

                convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage_surcharge':
                        price = (price + (price * (rule.percent_price / 100))) or 0.0
                        # _logger.debug('cup percentage_surcharge price >>>: %s', price)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
                if suitable_rule.base == 'standard_price':
                    # The cost of the product is always in the company currency
                    price = product.cost_currency_id.compute(price, self.currency_id, round=False)
                    # _logger.debug('cup standard_price price >>>: %s', price)
                else:
                    price = product.currency_id.compute(price, self.currency_id, round=False)
                    # _logger.debug('cup standard_price else price >>>: %s', price)

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)

        return results
        return res


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    _defaults = {'base': 1}

    # UNNECESSARY with current setup
    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     if 'product_default_code' or 'product_id' or 'product_tmpl_id' in groupby:
    #         fields.remove('min_quantity')
    #         fields.remove('price_sale')
    #         fields.remove('price_unit')
    #         fields.remove('margin_sale_net')
    #         fields.remove('margin_sale_excl')
    #         fields.remove('cost_product')
    #     return super(ProductPricelistItem, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    @api.onchange('compute_price')
    def onchange_compute_price(self):
        for item in self:
            item.base == 'standard_price'

    @api.onchange('product_tmpl_id', 'product_id')
    def onchange_product(self):
        for item in self:
            item.description = item.product_tmpl_id.display_name or item.product_id.display_name
    
    @api.depends('product_tmpl_id',
                 'product_tmpl_id.uom_pack_id', 
                 'product_id',
                 'product_id.uom_pack_id')
    @api.one
    def _compute_uom_pack_id(self):
        self.ensure_one()
        # _logger.debug('c_uom_pack call >>>: %s', self)
        product = False
        # check if product is set
        if self.applied_on == '1_product':
            product = self.product_tmpl_id
        if self.applied_on == '0_product_variant':
            product = self.product_id
        # set standard price for product            
        if product:
            # _logger.debug('c_uom_pack if upack >>>: %s', product.uom_pack_id)
            self.uom_pack_id = product.uom_pack_id
    
    @api.depends('applied_on',
                 'product_tmpl_id',
                 'product_id',
                 'base',
                 'base_pricelist_id',
                 'compute_price',
                 'min_quantity',
                 'uom_pack_id')
    @api.multi
    def _calc_price_unit(self):
        # TO DO: on-the-fly compute crashes on dummy record (NewId).
        # find a way to compute or add User/ValidationError to
        # warn user when editing rules from pricelist instead of item.
        # ¿¿ assign empty value to void dummy record NewId error ??
        for item in self:
            product = False
            quantity = item.min_quantity
            partner = False
            if item.applied_on == '1_product':
                product = item.product_tmpl_id
            if item.applied_on == '0_product_variant':
                product = item.product_id
            if product:
                price = item.pricelist_id.with_context(item_ids=item).get_product_price(
                    product, quantity, partner, date=False, uom_id=False)
                pack_factor = item.uom_pack_id.factor_inv
                item.price_unit = price
                item.price_sale = price * quantity
                item.price_pack = price * pack_factor
                # _logger.debug('_cp price prod_int_ref >>>: %s', product.default_code)
                # _logger.debug('_cp pack_factor >>>: %s', pack_factor)
                # _logger.debug('_cp price >>>: %s', price)

    @api.depends('product_tmpl_id', 
                 'product_id')
    @api.one
    def _compute_cost_product(self):
        self.ensure_one()
        product = False
        # check if product is set
        if self.applied_on == '1_product':
            product = self.product_tmpl_id
        if self.applied_on == '0_product_variant':
            product = self.product_id
        # set standard price for product            
        if product:
            if product.standard_price == 0:
                valuation = sum([variant._sum_remaining_values()[0] for variant in product])
                # _logger.debug('cost_product product_tmpl_id >>>: %s', self.product_tmpl_id)
                # _logger.debug('cost_product product_id >>>: %s', self.product_id)
                # _logger.debug('cost_product val >>>: %s', valuation)
                qty_available = product.with_context(company_owned=True).qty_available
                if qty_available:
                    standard_price = valuation / qty_available
                self.cost_product = standard_price
            else:
                # _logger.debug('cost_product val else >>>: %s', self)
                # _logger.debug('cost_product val else prod.sp >>>: %s', product.default_code)
                # _logger.debug('cost_product val else prod.sp >>>: %s', product.standard_price)
                self.cost_product = product.standard_price

    @api.depends('cost_product', 'margin_sale_excl')
    @api.one
    def _calc_margin_sale_net(self):
        self.ensure_one()
        if self.cost_product == 0.0:
            # _logger.debug('margin_sale if call >>>: %s', self)
            return {
                'warning': {'title': _('Input Error'),
                            'message': _('Net sale margin calculation will be set to 0 when product cost is 0.'), },
            }
        else:
            margin_sale_net = (self.price_unit * (100 - (self.margin_sale_excl % 100))) % self.cost_product
            self.margin_sale_net = ((margin_sale_net) - 1) * 100

    # exclusion constrain no longer necessary with new equation logic
    # REMOVE after testing
    # @api.constrains('margin_sale_excl')
    # def _check_margin_exclusion_percent(self):
    #     if 0 >= self.margin_sale_excl >= 1:
    #         raise ValidationError(
    #             "Sale margin exclusion must be greater than or equal 0 and less than or equal to 1.")

    active_pricelist = fields.Boolean(
        related='pricelist_id.active',
        string="Active",
        readonly=True)

    is_hidden = fields.Boolean(
        related='pricelist_id.is_hidden',
        string="Hide item",
        default=False,
        help='Don\'t show item in product price.')

    product_default_code = fields.Char(
        related='product_id.default_code',
        string="Product Code",
        help='Product default code.',
        readonly=True)

    description = fields.Char(
        string='Description',
        help='Pricelist item description.')
    
    partner_ids = fields.Many2many(
        related='pricelist_id.partner_ids',
        string="Partners")
    
    uom_pack_id = fields.Many2one(
        'product.uom', 
        compute='_compute_uom_pack_id', 
        readonly=True, 
        help="Package Unit of Measure to factor package price.")

    compute_price = fields.Selection([
        ('fixed', 'Fix Price'),
        ('percentage', 'Percentage (discount)'),
        ('percentage_surcharge', 'Percentage (surcharge)'),
        ('formula', 'Formula')], index=True, default='percentage_surcharge')

    price_unit = fields.Monetary(
        string='Unit Price',
        currency_field='currency_id',
        compute='_calc_price_unit',
        readonly=True,
        store=True,
        help='Unit Price for current item.')

    price_sale = fields.Monetary(
        string='Sale Price',
        currency_field='currency_id',
        compute='_calc_price_unit',
        readonly=True,
        store=True,
        help='Sale Price for current item.')

    price_pack = fields.Monetary(
        string='Package Sale Price',
        currency_field='currency_id',
        compute='_calc_price_unit',
        readonly=True,
        store=True,
        help='Package Sale Price for current item.')

    cost_product = fields.Float(
        string="Product Cost",
        compute='_compute_cost_product',
        readonly=True,
        store=True,
        help='Cost price based on product\'s Standard Price.')

    margin_sale_net = fields.Float(
        string='Net Sale Margin %',
        compute='_calc_margin_sale_net',
        readonly=True,
        store=True,
        help='Net sale margin for current item (factored by sale margin exclusion).')

    margin_sale_excl = fields.Float(
        string='Excl. %',
        default=16.00,
        help='Sale margin exclusion percent.')
