# -*- coding: utf-8 -*-
# import logging

from itertools import chain
from odoo import models, fields, api, _
from datetime import datetime
import odoo.addons.decimal_precision as dp

from odoo.exceptions import UserError

# _logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    partner_ids = fields.Many2many("res.partner", string="Partners")
    item_product_default_code = fields.Char(
        related="item_ids.product_default_code",
        string="Product Internal Reference",
        help="Product's default code.",
        readonly=True,
    )
    is_hidden = fields.Boolean(
        string="Hide items",
        default=False,
        help="Hide from product price view. Helpful if using pricelist only to perform calculations on other pricelists.",
    )

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        res = super(ProductPricelist, self)._compute_price_rule(
            products_qty_partner, date=False, uom_id=False
        )

        self.ensure_one()
        if not date:
            date = self._context.get("date") or fields.Date.context_today(self)
        if not uom_id and self._context.get("uom"):
            uom_id = self._context["uom"]
        if uom_id:
            # rebrowse with uom if given
            products = [
                item[0].with_context(uom=uom_id) for item in products_qty_partner
            ]
            products_qty_partner = [
                (products[index], data_struct[1], data_struct[2])
                for index, data_struct in enumerate(products_qty_partner)
            ]
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
            prod_ids = [
                p.id
                for p in list(
                    chain.from_iterable([t.product_variant_ids for t in products])
                )
            ]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            "SELECT item.id "
            "FROM product_pricelist_item AS item "
            "LEFT JOIN product_category AS categ "
            "ON item.categ_id = categ.id "
            "WHERE (item.product_tmpl_id IS NULL OR item.product_tmpl_id = any(%s))"
            "AND (item.product_id IS NULL OR item.product_id = any(%s))"
            "AND (item.categ_id IS NULL OR item.categ_id = any(%s)) "
            "AND (item.pricelist_id = %s) "
            "AND (item.date_start IS NULL OR item.date_start<=%s) "
            "AND (item.date_end IS NULL OR item.date_end>=%s)"
            "ORDER BY item.applied_on, item.min_quantity desc, categ.parent_left desc",
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date),
        )

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env["product.pricelist.item"].browse(item_ids)
        if self._context.get("item_ids"):
            item_ids = [self._context.get("item_ids", [])]
            items = item_ids
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get("uom") or product.uom_id.id
            price_uom_id = product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = (
                        self.env["product.uom"]
                        .browse([self._context["uom"]])
                        ._compute_quantity(qty, product.uom_id)
                    )
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute("list_price")[product.id]

            price_uom = self.env["product.uom"].browse([qty_uom_id])
            for rule in items:
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    # bypass min_qty restrict for gard_product_price.product_pricelist_item_tree_view
                    if item_ids:
                        pass
                    else:
                        continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (
                        product.product_variant_count == 1
                        and product.product_variant_id.id == rule.product_id.id
                    ):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if (
                        rule.product_tmpl_id
                        and product.product_tmpl_id.id != rule.product_tmpl_id.id
                    ):
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

                if rule.base == "pricelist" and rule.base_pricelist_id:
                    price_tmp = rule.base_pricelist_id._compute_price_rule(
                        [(product, qty, partner)], date, uom_id
                    )[product.id][
                        0
                    ]  # TDE: 0 = price, 1 = rule
                    price = rule.base_pricelist_id.currency_id.compute(
                        price_tmp, self.currency_id, round=False
                    )
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = lambda price: product.uom_id._compute_price(
                    price, price_uom
                )

                if price is not False:
                    if rule.compute_price == "fixed":
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == "percentage_surcharge":
                        price = (price + (price * (rule.percent_price / 100))) or 0.0
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if (
                suitable_rule
                and suitable_rule.compute_price != "fixed"
                and suitable_rule.base != "pricelist"
            ):
                if suitable_rule.base == "standard_price":
                    # The cost of the product is always in the company currency
                    price = product.cost_currency_id.compute(
                        price, self.currency_id, round=False
                    )
                else:
                    price = product.currency_id.compute(
                        price, self.currency_id, round=False
                    )

            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
            return results
        return res


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _defaults = {"base": 1}

    @api.one
    def write(self, vals):
        res = super(ProductPricelistItem, self).write(vals)
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")
        uom_pack_id = vals.get("uom_pack_id")
        price_unit = vals.get("price_unit")
        product = False
        # force recompute for global items
        if uom_pack_id:
            if self.applied_on == "3_global":
                if active_id and active_model in (
                    "product.product",
                    "product.template",
                ):
                    product = self.env[active_model].search([("id", "=", active_id)])
                    self.write({"global_uom_pack_id": uom_pack_id})
        # force recompute on csv import by updating date_update field
        # on related base_pricelist_id items
        if price_unit:
            if self.applied_on in ["1_product", "0_product_variant"]:
                product = self.product_tmpl_id or self.product_id
                rel_pricelist_items = self.search(
                    [
                        "|",
                        ("product_tmpl_id", "=", product.id),
                        ("product_id", "=", product.id),
                    ]
                )
                recompute_items = rel_pricelist_items
                if recompute_items:
                    for r_item in recompute_items:
                        r_item.write(
                            {
                                "date_update": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            }
                        )
        return res

    # @api.model
    # def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     _logger.debug('read_group call init self >>>: %s', self)
    #     _logger.debug('read_group call init self._fields >>>: %s', self._fields)
    #     f_list = list()
    #     for k, v in self._fields.items():
    #         if k == "applied_on":
    #             f_list.append(v)
                
    #         _logger.debug('read_group call init _fields f_list >>>: %s', f_list)
    #     # _logger.debug('read_group call init self._fields >>>: %s', self._fields.product_id)
    #     # for item in self._fields:
    #     #     _logger.debug('read_group call init for item >>>: %s', item)
    #     #     for product_tmpl in item.product_tmpl_id:
    #     #         _logger.debug('read_group call for product_tmpl >>>: %s', product_tmpl)
    #             # product_tmpl
    #     _logger.debug('read_group call init self._context >>>: %s', self._context)
    #     _logger.debug('read_group call init self._context.get(params) >>>: %s', self._context.get('params'))
    #     _logger.debug('read_group call init self._context.get(params).get(view_type) >>>: %s', self._context.get('params').get('view_type'))
    #     get_view_type = self._context.get('params').get('view_type')
    #     # get_group_by = self._context.get('params').get('group_by')
    #     _logger.debug('read_group call init >>>: %s', domain)
    #     _logger.debug('read_group call init >>>: %s', fields)
    #     _logger.debug('read_group call init >>>: %s', groupby)
    #     _logger.debug('read_group call init >>>: %s', offset)
    #     _logger.debug('read_group call init >>>: %s', limit)
    #     _logger.debug('read_group call init >>>: %s', orderby)
    #     # search and show all products when a rule applied_on == 'global'
    #     if get_view_type == 'pivot':
    #         _logger.debug('read_group call if get_view_type >>>: %s', get_view_type)
    #         _logger.debug('read_group call if get_view_type fields >>>: %s', fields)
    #         _logger.debug('read_group call if get_view_type group_by >>>: %s', groupby)
    #         if 'pricelist_id' and 'product_id' in fields:
    #             _logger.debug('read_group call if groupby >>>: %s', groupby)
    #             _logger.debug('read_group call if groupby domain.get(a_on) >>>: %s', [d['applied_on'] for d in domain])
    #             # list(map(lambda x: x[], domain)))
    #             fields.remove('__count')
    #             # for item in self:
    #             if 'global' in list(map(lambda x: x['applied_on'], domain)):
    #                 _logger.debug('read_group call if a_on global domain >>>: %s', fields)

    #     # this was from a previous development; currently not used
    #     # if 'product_default_code' or 'product_id' or 'product_tmpl_id' in groupby:
    #     #     fields.remove('min_quantity')
    #     #     fields.remove('price_sale')
    #     #     fields.remove('price_unit')
    #     #     fields.remove('margin_sale_net')
    #     #     fields.remove('margin_sale_excl')
    #     #     fields.remove('cost_product')
    #     return super(ProductPricelistItem, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)

    # @api.model
    # def _read_group_raw(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
    #     res = super(ProductPricelistItem, self)._read_group_raw(domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True)

    #     return res

    @api.onchange("compute_price")
    def onchange_compute_price(self):
        self.base == "standard_price"

    @api.onchange("product_tmpl_id", "product_id")
    def onchange_product(self):
        self.description = (
            self.product_tmpl_id.display_name or self.product_id.display_name
        )

    @api.depends(
        "product_tmpl_id",
        "product_tmpl_id.uom_pack_id",
        "product_id",
        "product_id.uom_pack_id",
    )
    @api.one
    def _compute_uom_pack_id(self):
        product = False
        uom_pack_id = False
        applied_on_product = False
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")
        # check if product is set
        if self.applied_on == "3_global":
            if active_id and active_model in (
                "product.product",
                "product.template",
            ):
                product = self.env[active_model].search([("id", "=", active_id)])
                self.write({"uom_pack_id": False})
        if self.applied_on in ["1_product", "0_product_variant"]:
            applied_on_product = True
            product = self.product_tmpl_id or self.product_id
            uom_pack_id = product.uom_pack_id
        if product:
            self.uom_pack_id = uom_pack_id
            if applied_on_product:
                self.global_uom_pack_id = False
            else:
                self.global_uom_pack_id = product.uom_pack_id

    @api.depends(
        "applied_on",
        "base",
        "base_pricelist_id",
        "compute_price",
        "percent_price",
        "min_quantity",
        "date_update",
        "uom_pack_id",
    )
    @api.one
    def _calc_price_unit(self):
        # TO DO: on-the-fly compute crashes on dummy record (NewId).
        # find a way to compute or add User/ValidationError to
        # warn user when editing rules from pricelist instead of item.
        # ¿¿ assign empty value to void dummy record NewId error ??
        product = False
        quantity = self.min_quantity
        pack_factor = self.uom_pack_id.factor_inv
        partner = False
        active_id = self.env.context.get("active_id")
        active_model = self.env.context.get("active_model")
        if self.applied_on == "3_global":
            if active_id and active_model in (
                "product.product",
                "product.template",
            ):
                product = self.env[active_model].search([("id", "=", active_id)])
                pack_factor = product.uom_pack_id.factor_inv
        if self.applied_on in ["1_product", "0_product_variant"]:
            product = self.product_tmpl_id or self.product_id
        if product:
            price = self.pricelist_id.with_context(item_ids=self).get_product_price(
                product, quantity, partner, date=False, uom_id=False
            )
            pack_factor = pack_factor
            self.price_unit = price
            self.price_sale = price * quantity
            self.price_pack = price * pack_factor
            self.product_global_id = product

    @api.depends("product_tmpl_id", "product_id", "product_id.stock_value")
    @api.one
    def _compute_cost_product(self):
        product = False
        # check if product is set
        if self.applied_on in ["1_product", "0_product_variant"]:
            product = self.product_tmpl_id or self.product_id
        # get product standard price or inventory valuation
        if product:
            if product.standard_price == 0:
                valuation = product.stock_value
                qty_available = product.qty_at_date
                if qty_available:
                    standard_price = valuation / qty_available
                self.cost_product = standard_price
            else:
                self.cost_product = product.standard_price

    @api.depends("cost_product", "margin_sale_excl")
    @api.one
    def _calc_margin_sale_net(self):
        if self.cost_product == 0.0:
            self.margin_sale_net == 0.0
            return {
                "warning": {
                    "title": _("Input Error"),
                    "message": _(
                        "Division by zero cannot be performed. Net sale margin calculation will be set to 0 when product cost is 0."
                    ),
                },
            }
        else:
            margin_sale_net = (
                self.price_unit * (100 - (self.margin_sale_excl % 100))
            ) % self.cost_product
            self.margin_sale_net = ((margin_sale_net) - 1) * 100

    active_pricelist = fields.Boolean(
        related="pricelist_id.active", string="Active", readonly=True, help="Checks pricelist's active state.",
    )
    is_hidden = fields.Boolean(
        related="pricelist_id.is_hidden",
        string="Hide item",
        default=False,
        help="Hide item in product price view.",
    )
    product_default_code = fields.Char(
        related="product_id.default_code",
        string="Product Code",
        readonly=True,
        help="Product's default code.",
    )
    description = fields.Char(string="Description", help="Pricelist item description.")
    partner_ids = fields.Many2many(
        related="pricelist_id.partner_ids",
        string="Partners",
        help="Related partners.",
    )
    date_update = fields.Datetime(
        "Updated Date",
        # compute="_calc_price_unit",
        copy=False,
        readonly=True,
        # store=True,
        help="Date item was last updated.",
    )
    uom_pack_id = fields.Many2one(
        "product.uom",
        compute="_compute_uom_pack_id",
        readonly=True,
        store=True,
        help="Package Unit of Measure to factor package price.",
    )
    global_uom_pack_id = fields.Many2one(
        "product.uom",
        compute="_compute_uom_pack_id",
        readonly=True,
        # store=True,
        help="Global Package Unit of Measure to factor package price for global items.",
    )
    compute_price = fields.Selection(
        [
            ("fixed", "Fix Price"),
            ("percentage", "Percentage (discount)"),
            ("percentage_surcharge", "Percentage (surcharge)"),
            ("formula", "Formula"),
        ],
        index=True,
        default="percentage_surcharge",
    )
    price_unit = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
        compute="_calc_price_unit",
        readonly=True,
        store=True,
    )
    price_pack = fields.Monetary(
        string="Package Sale Price",
        currency_field="currency_id",
        compute="_calc_price_unit",
        readonly=True,
        store=True,
        help="Package Sale Price.",
    )
    cost_product = fields.Float(
        string="Product Cost",
        compute="_compute_cost_product",
        readonly=True,
        store=True,
        help="Cost price based on product's Standard Price (when set) or inventory valuation.",
    )
    margin_sale_net = fields.Float(
        string="Net Sale Margin %",
        compute="_calc_margin_sale_net",
        readonly=True,
        store=True,
        help="Net sale margin (factored by sale margin exclusion).",
    )
    margin_sale_excl = fields.Float(
        string="Excl. %", default=16.00, help="Sale margin exclusion percent."
    )
