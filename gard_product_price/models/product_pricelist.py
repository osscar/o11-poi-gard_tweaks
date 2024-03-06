# -*- coding: utf-8 -*-
import logging

from itertools import chain
from odoo import fields, models, api, _
from datetime import datetime

from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _name = "product.pricelist"
    _inherit = ["product.pricelist", 'mail.thread', 'mail.activity.mixin']

    partner_ids = fields.Many2many("res.partner", string="Partners", track_visibility="onchange",)
    item_product_default_code = fields.Char(
        string="Product Internal Reference",
        related="item_ids.product_default_code",
        readonly=True,
        help="Product's default code.",
        track_visibility="onchange",
    )
    is_hidden = fields.Boolean(
        string="Hide",
        default=False,
        help="Hide from product price view. Helpful if using pricelist only to perform calculations on other pricelists.",
        track_visibility="onchange",
    )
    date_update = fields.Datetime(
        string="Updated Date",
        readonly=True,
        copy=False,
        help="Date last updated.",
        track_visibility="onchange",
    )

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
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
        else:
            res = super(ProductPricelist, self)._compute_price_rule(
            products_qty_partner, date=date, uom_id=uom_id
        )
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
    _name = "product.pricelist.item"
    _inherit = ["product.pricelist.item", 'mail.thread', 'mail.activity.mixin']
    _defaults = {"base": 1}

    active_pricelist = fields.Boolean(
        related="pricelist_id.active",
        readonly=True,
        help="Checks pricelist's active state.",
        track_visibility="onchange",
    )
    pricelist_id = fields.Many2one(track_visibility="always")
    base_pricelist_id = fields.Many2one(track_visibility="always")
    percent_price = fields.Float(track_visibility="onchange")
    min_quantity = fields.Integer(track_visibility="onchange")
    is_hidden = fields.Boolean(
        related="pricelist_id.is_hidden",
        default=False,
        help="Hide item in product price view.",
        track_visibility="onchange",
    )
    product_default_code = fields.Char(
        related="product_id.default_code",
        string="Product Code",
        readonly=True,
        help="Product's default code.",
        track_visibility="onchange",
    )
    description = fields.Char(string="Description", help="Pricelist item description.")
    partner_ids = fields.Many2many(
        related="pricelist_id.partner_ids",
        help="Related partners.",
        track_visibility="onchange",
    )
    date_update = fields.Datetime(
        string="Updated Date",
        compute="_sale_price",
        # related="base_pricelist_id.date_update",
        # copy=False,
        # readonly=True,
        store=True,
        help="Date item was last updated.",
        track_visibility="onchange",
    )
    min_quantity_uom_id = fields.Many2one(
        "product.uom",
        string="UoM",
        compute="_compute_uoms",
        readonly=True,
        store=True,
        help="Minimum Quantity UoM.",
    )
    uom_pack_id = fields.Many2one(
        "product.uom",
        string="Pack UoM",
        compute="_compute_uoms",
        readonly=True,
        store=True,
        help="Package Unit of Measure to factor package price.",
    )
    min_quantity_pack = fields.Integer(
        "Pack Min. Qty.",
        compute="_compute_uoms",
        readonly=True,
        store=True,
        help="Pack minimum quantity.",
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
        track_visibility="onchange",
    )
    price_unit = fields.Monetary(
        string="Unit Price",
        currency_field="currency_id",
        compute="_sale_price",
        readonly=True,
        store=True,
        track_visibility="onchange",
    )
    price_pack = fields.Monetary(
        string="Pack Price",
        currency_field="currency_id",
        compute="_sale_price",
        readonly=True,
        store=True,
        help="Package Sale Price.",
    )
    price_recompute = fields.Boolean(
        string="Recompute Related",
        default=False,
        help="Recompute related items. Select to recompute.",
    )
    product_cost = fields.Monetary(
        string="Product Cost",
        related="product_id.stock_value_unit",
        help="Cost price per default product UoM, based on product's Standard Price (when set) or inventory valuation.",
        track_visibility="onchange",
    )
    margin_sale_net_unit = fields.Monetary(
        string="Unit Margin Net",
        currency_field="currency_id",
        compute="_compute_sale_margin",
        readonly=True,
        store=True,
        help="Net sale margin (including margin exclusion).",
        track_visibility="onchange"
    )
    margin_sale_net_pack = fields.Monetary(
        string="Pack Margin Net",
        currency_field="currency_id",
        compute="_compute_sale_margin",
        readonly=True,
        store=True,
        help="Net sale margin (including margin exclusion).",
    )
    margin_sale_net_factor = fields.Float(
        string="Factor Margin Net",
        compute="_compute_sale_margin",
        readonly=True,
        store=True,
        help="Net sale margin factor (including margin exclusion).",
        track_visibility="onchange",
    )
    margin_sale_excl = fields.Float(
        string="Margin Excluded", default=16.00, help="Sale margin exclusion percent.", track_visibility="onchange",
    )

    def _get_warning_msg(self):
        warning = {}
        if self._context.get("warning") == "zero_div":
            warning = {
                        "warning": {
                            "title": _("Input Error"),
                            "message": _(
                                "Division by zero cannot be performed. Net sale margin calculation will be set to 0 when product cost is 0."
                            ),
                        },
                    }
        elif self._context.get("warning") == "recompute":
            warning = {
                        "warning": {
                            "title": _("Recompute"),
                            "message": _(
                                "If you continue, all affected pricelist items \
                                by the changes made to this record, will be recomputed. \
                                This could take a long time depending on the amount of records being processed."
                            ),
                        },
                    }
        return warning

    @api.onchange("compute_price")
    def onchange_sale_price(self):
        self.base == "standard_price"

    @api.onchange("price_recompute")
    def onchange_price_recompute(self):
        if self.price_recompute:
            return self.with_context(warning="recompute")._get_warning_msg()
    
    @api.depends(
        "min_quantity",
        "product_tmpl_id.uom_pack_id",
        "product_id.uom_pack_id",
    )
    @api.multi
    def _compute_uoms(self):
        vals = []
        for item in self:
            uom_id = False
            # product = False
            uom_pack_id = False
            min_qty_pack = 0.0
            # check if product is set
            if item.applied_on == "3_global":
                active_id = self.env.context.get("active_id")
                active_model = self.env.context.get("active_model")
                if active_id and active_model in (
                    "product.product",
                    "product.template",
                ):
                    product = self.env[active_model].search([("id", "=", active_id)])
            if item.applied_on in ["1_product", "0_product_variant"]:
                if item.applied_on == "1_product":
                    product = item.product_tmpl_id
                elif item.applied_on == "0_product_variant":
                    product = item.product_id
                uom_pack_id = product.uom_pack_id
                min_qty = item.min_quantity
                uom_id = product.uom_id
                if uom_id.category_id == uom_pack_id.category_id:
                    uom_pack_factor = uom_pack_id.factor_inv
                    min_qty_pack = min_qty / uom_pack_factor
                else:
                    raise ValidationError(
                        _(
                            "Error! Min. Qty UoM and Pack UoM have different categories. Pack minimum quantity cannot be computed."
                        )
                    )
                vals = {
                    "min_quantity_uom_id": uom_id,
                    "uom_pack_id": uom_pack_id,
                    "min_quantity_pack": min_qty_pack,
                }
            item.update(vals)


    @api.depends(
        "base",
        "base_pricelist_id",
        "pricelist_id",
        "compute_price",
        "percent_price",
        "uom_pack_id",
        "product_cost",
        # "date_update",
    )
    @api.multi
    def _sale_price(self):
        vals = {}
        # .filtered(lambda i: i.applied_on != "3_global")
        for item in self.filtered(lambda i: i.applied_on != "3_global"):
            # vals = {}
            price = 0.0
            product_id = False
            pack_factor = item.uom_pack_id.factor_inv
            price_pack = 0.0
            pricelist_id = item.pricelist_id
            partner_ids = item.partner_ids
            date = fields.Datetime.now()
            qty = item.min_quantity
            if item.applied_on == "3_global":
                active_id = self.env.context.get("active_id")
                active_model = self.env.context.get("active_model")
                if active_id and active_model in (
                    "product.product",
                    "product.template",
                ):
                    product_id = self.env[active_model].search([("id", "=", active_id)])
                    pack_factor = product_id.uom_pack_id.factor_inv
            elif item.applied_on in ["1_product", "0_product_variant"]:
                if item.applied_on == "1_product":
                    product_id = item.product_tmpl_id
                elif item.applied_on == "0_product_variant":
                    product_id = item.product_id
            price = pricelist_id.with_context(item_ids=item).get_product_price(product=product_id, quantity=qty, partner=partner_ids, date=False, uom_id=False)
            _logger.debug("_csp dict list price >>>: %s", price)
            _logger.debug("_csp dict list pack_factor >>>: %s", pack_factor)
            price_pack = price * pack_factor
            _logger.debug("_csp price post>>>: %s", price)
            vals = {
            "price_unit": price,
            "price_pack": price_pack,
            "date_update": date,
            }
            _logger.debug("_csp item vals post >>>: %s", vals)
        self.update(vals)

    @api.depends("price_unit", "margin_sale_excl")
    @api.multi
    def _compute_sale_margin(self):
        vals = {}
        for item in self:
            product_cost = item.product_cost
            margin_sale_net_unit = 0.0
            margin_sale_net_pack = 0.0
            margin_sale_net_factor = 0.0
            if product_cost == 0.0:
                vals = {
                "margin_sale_net_unit": margin_sale_net_unit,
                "margin_sale_net_pack": margin_sale_net_pack,
                "margin_sale_net_factor": margin_sale_net_factor,
                }
            else:
                uom_factor_inv = item.uom_pack_id.factor_inv
                price_unit = item.price_unit
                margin_sale_excl = 1 - (item.margin_sale_excl / 100)
                margin_sale_net_unit = (price_unit * margin_sale_excl) - product_cost
                margin_sale_net_pack =  (margin_sale_net_unit * uom_factor_inv)
                margin_sale_net_factor = margin_sale_net_unit / product_cost
            vals = {
                "margin_sale_net_unit": margin_sale_net_unit,
                "margin_sale_net_pack": margin_sale_net_pack,
                "margin_sale_net_factor": margin_sale_net_factor,
                }
            item.update(vals)
                
    def _get_related_items(self, product, applied_on, pricelists):
        domain = [('base_pricelist_id','=',pricelists.id)]
        domain_pricelist = [('id','!=',self.id), ('active_pricelist','=',True), ('base_pricelist_id','=',pricelists.id)]
        domain_product = [('product_id','=',product.id)]
        ritems = self.env['product.pricelist.item']
        if product or pricelists:
            ritem_search = self.env['product.pricelist.item']
            # pricelist_search = self.env['product.pricelist']    
            if applied_on == "0_product_variant":
                domain += domain_product
                # product_search = product
            ritem_search = self.env['product.pricelist.item']
            pricelist_search = pricelists + self.base_pricelist_id
            _logger.debug("_gri domain >>>: %s", domain)
            _logger.debug("_gri self >>>: %s", (self, product, applied_on, pricelists))
            count_ritems = len(self.env['product.pricelist'].search([]))
            _logger.debug("_gri if count_ritems >>>: %s", count_ritems)
            while count_ritems >= 0:
                ritem_search = self.env['product.pricelist.item'].search(domain)
                _logger.debug("_gri while ritem_search >>>: %s", len(ritem_search))
                ritems |= ritem_search
                for rsitem in ritem_search:
                    # product_search |= rsitem.product_id
                    pricelist_search |= rsitem.pricelist_id + rsitem.base_pricelist_id
                _logger.debug("_gri while if pricelist_search post >>>: %s", pricelist_search)
                pricelists |= pricelist_search
                _logger.debug("_gri while pricelists post >>>: %s", pricelists)
                del domain[:]
                # if pricelist_search:
                # domain_product = [('product_id','in',([prod.id for prod in product_search]))]
                domain_pricelist = [('id','!=',self.id), ('active_pricelist','=',True), ('base_pricelist_id','in',([plist.id for plist in pricelists]))]
                domain = domain_pricelist
                # if applied_on == "3_global":
                #     pricelist_search |= pricelists
                #     # count_ritems += 2
                if applied_on == "0_product_variant":
                    domain += domain_product
                    _logger.debug("_gri if product domain >>>: %s", domain)
                _logger.debug("_gri while count_ritems >>>: %s", count_ritems)
                ritem_search = self.env['product.pricelist.item']
                pricelist_search = self.env['product.pricelist']    
                if not ritem_search:
                    count_ritems -= 1
        return ritems, pricelists

    # @api.model
    def _recompute_items(self):
        self.ensure_one()
        # avoid infinite loop by switching recompute field to False
        self.price_recompute = False
        # get related items by product
        ritem_ids, pricelist_ids = self._get_related_items(product=self.product_id, applied_on=self.applied_on, pricelists=self.pricelist_id)
        date = fields.Datetime.now()
        # force recompute by updating date_update field
        ritem_ids = ritem_ids.filtered(lambda ritem: ritem.applied_on != "3_global")
        # .(ritem.pricelist_id.id, ritem.id)
        # ritem_ids._recompute_todo(self._fields['uom_pack_id'])
        # ritem_ids._recompute_todo(self._fields['price_unit'])
        for ritem in ritem_ids:
            ritem._onchange_applied_on()
            # _write({"price_unit": ritem.price_unit})
        # self.recompute()
        _logger.debug("reci ritems post >>>: %s", len(ritem_ids))
        _logger.debug("reci for ritem pricelist_ids >>>: %s", pricelist_ids)
        return date, pricelist_ids
        
    @api.multi
    def _write(self, vals):
        res = super()._write(vals)
        pricelist_ids = self.env['product.pricelist.item']
        # item_ids = self.env['product.pricelist']
        date = False
        # log update on base pricelist log
        # with self.env.norecompute():
        for item in self.filtered(lambda i: i.price_recompute):
            # run recompute on related items 
            # and get related pricelists and update date
            date, pricelist_ids = item._recompute_items()
            item_ids = item
            pricelist_ids |= item.pricelist_id
            # item_ids._recompute_todo(self._fields['uom_pack_id'])
        pricelist_ids.update({"date_update": date})
        return res