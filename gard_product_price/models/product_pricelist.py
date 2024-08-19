# -*- coding: utf-8 -*-
# import logging

from itertools import chain
from odoo import fields, models, api, _
from datetime import datetime

from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


# _logger = logging.getLogger(__name__)


class ProductPricelist(models.Model):
    _name = "product.pricelist"
    _inherit = ["product.pricelist", "mail.thread", "mail.activity.mixin"]

    partner_ids = fields.Many2many(
        "res.partner",
        string="Partners",
        track_visibility="onchange",
    )
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
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
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

        if self._context.get("item_id"):
            item_ids = [self._context.get("item_id").id]

        items = self.env["product.pricelist.item"].browse(item_ids)
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
            # product_cost_base = price

            price_uom = self.env["product.uom"].browse([qty_uom_id])
            for rule in items:
                product_cost_base = price
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
                    product_cost_base = price
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    price = product.price_compute(rule.base)[product.id]
                    product_cost_base = rule.product_cost
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
            if suitable_rule:
                if (
                    suitable_rule.base == "pricelist"
                    and suitable_rule.applied_on == "0_product_variant"
                ):
                    # suitable_rule.product_cost_base = product_cost_base
                    # product_cost_base = rule.product_cost
                    if suitable_rule.base_pricelist_id.tax_ids:
                        base_pricelist = suitable_rule.base_pricelist_id
                        # sale_taxes = tax_ids.filtered(lambda t: t.type_tax_use == 'sale')
                        taxes = base_pricelist.tax_ids.compute_all(
                            product_cost_base,
                            base_pricelist.currency_id,
                            qty,
                            product=product,
                            partner=base_pricelist.partner_ids,
                        )
                        if taxes:
                            product_cost_base = taxes["total_excluded"]
                    suitable_rule._write({"product_cost_base": product_cost_base})
            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
            return results
        return res

    # def get_product_price_rule(self, product, quantity, partner, date=False, uom_id=False):
    #     """ For a given pricelist, return price and rule for a given product """
    #     # _logger.debug('gppr self._context >>>: %s', self._context)
    #     self.ensure_one()
    #     _logger.debug('gppr self._context >>>: %s', self._context)
    #     context = self._context
    #     return super().with_context(context).get_product_price_rule(product, quantity, partner, date=False, uom_id=False)


class ProductPricelistItem(models.Model):
    _name = "product.pricelist.item"
    _inherit = ["product.pricelist.item", "mail.thread", "mail.activity.mixin"]
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
        # compute="_sale_price",
        # related="base_pricelist_id.date_update",
        # copy=False,
        readonly=True,
        # store=True,
        help="Date item was last updated.",
        track_visibility="onchange",
    )
    product_uom = fields.Many2one(
        "product.uom",
        string="Product UoM",
        related="product_id.uom_id",
        readonly=True,
        # store=True,
        # oldname="min_quantity_uom_id",
        help="Minimum Quantity UoM.",
    )
    product_uom_pack = fields.Many2one(
        "product.uom",
        string="Pack UoM",
        related="product_id.uom_pack_id",
        readonly=True,
        # store=True,
        oldname="uom_pack_id",
        help="Package Unit of Measure to factor package price.",
    )
    min_quantity_pack = fields.Integer(
        "Pack Min. Qty.",
        # compute="_compute_uoms",
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
    fixed_price = fields.Float(
        "Fixed Price", digits=dp.get_precision("Product Price Extended")
    )
    fixed_price_pack = fields.Float(
        "Fixed Price Pack", digits=dp.get_precision("Product Price Extended")
    )
    price_unit = fields.Monetary(
        "Unit Price",
        currency_field="currency_id",
        compute="_compute_amount",
        readonly=True,
        store=True,
        digits=dp.get_precision("Product Price"),
        # default=0.0
    )
    price_net_unit = fields.Monetary(
        "Unit Net Price",
        currency_field="currency_id",
        compute="_compute_amount",
        readonly=True,
        store=True,
        digits=dp.get_precision("Product Price"),
        # default=0.0
    )
    tax_price_unit = fields.Float(
        compute="_compute_amount", string="Unit Taxes", readonly=True, store=True
    )
    price_pack = fields.Monetary(
        string="Pack Price",
        currency_field="currency_id",
        compute="_compute_amount",
        readonly=True,
        store=True,
        help="Package Sale Price.",
    )
    price_net_pack = fields.Monetary(
        string="Pack Net Price",
        currency_field="currency_id",
        compute="_compute_amount",
        readonly=True,
        store=True,
        help="Package Sale Price.",
    )
    tax_price_pack = fields.Float(
        compute="_compute_amount", string="Pack Taxes", readonly=True, store=True
    )
    price_recompute = fields.Boolean(
        string="Recompute Related",
        default=False,
        help="Recompute related items. Select to recompute.",
    )
    product_cost = fields.Monetary(
        string="Product Cost",
        currency_field="currency_id",
        compute="_product_cost",
        readonly=True,
        store=True,
        help="Cost price per default product UoM, based on product's Standard Price (when set) or inventory valuation.",
        track_visibility="onchange",
    )
    product_cost_base = fields.Monetary(
        string="Product Cost Base Price",
        currency_field="currency_id",
        compute="_compute_amount",
        readonly=True,
        help="Product cost base,based on base pricelist values.",
        track_visibility="onchange",
    )
    is_price_pack = fields.Boolean(
        string="Fixed Pack Price",
        default=False,
        help="Fixed price per pack, instead of per unit.",
    )
    margin_unit = fields.Monetary(
        string="Unit Margin",
        currency_field="currency_id",
        compute="_product_margin",
        readonly=True,
        store=True,
        help="Margin (including margin exclusion).",
        track_visibility="onchange",
    )
    margin_net_unit = fields.Monetary(
        string="Unit Net Margin",
        currency_field="currency_id",
        compute="_product_margin",
        readonly=True,
        store=True,
        help="Net margin (including margin exclusion).",
        oldname="margin_sale_net_unit",
        track_visibility="onchange",
    )
    margin_pack = fields.Monetary(
        string="Pack Margin",
        currency_field="currency_id",
        compute="_product_margin",
        readonly=True,
        store=True,
        # oldname="margin_sale_net_pack",
        help="Margin (including margin exclusion).",
    )
    margin_net_pack = fields.Monetary(
        string="Pack Net Margin",
        currency_field="currency_id",
        compute="_product_margin",
        readonly=True,
        store=True,
        oldname="margin_sale_net_pack",
        help="Net margin (including margin exclusion).",
    )
    margin_factor = fields.Float(
        string="Factor Margin",
        compute="_product_margin",
        readonly=True,
        store=True,
        # oldname="margin_sale_net_factor",
        help="Margin factor (including margin exclusion).",
        track_visibility="onchange",
    )
    margin_net_factor = fields.Float(
        string="Factor Net Margin",
        compute="_product_margin",
        readonly=True,
        store=True,
        oldname="margin_sale_net_factor",
        help="Net margin factor (including margin exclusion).",
        track_visibility="onchange",
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

    def _get_product(self):
        product = self.product_id or False
        applied_on = self.applied_on
        if applied_on == "3_global":
            active_id = self.env.context.get("active_id")
            active_model = self.env.context.get("active_model")
            if active_id and active_model in (
                "product.product",
                "product.template",
            ):
                product = self.env[active_model].search([("id", "=", active_id)])
        if applied_on in ["1_product", "0_product_variant"]:
            if self.applied_on == "1_product":
                product = self.product_tmpl_id
            elif self.applied_on == "0_product_variant":
                product = self.product_id
        return product

    def _get_price_unit(self, product, item, taxes, pricelist):
        sale_order_line_obj = self.env["sale.order.line"]
        date = fields.Date.today()
        product_context = dict(
            self.env.context, partner_id=False, date=date, uom=item.product_uom.id
        )
        base_price, currency_id = sale_order_line_obj.with_context(
            product_context
        )._get_real_price_currency(
            product, item.id, 1.0, item.product_uom, pricelist.id
        )

        price = base_price

        if item.is_price_pack:
            price = item.fixed_price_pack

        if taxes:
            price = self.env["account.tax"]._fix_tax_included_price_company(
                price, product.taxes_id, taxes, pricelist.company_id
            )

        return base_price, price

    @api.onchange("price_recompute")
    def onchange_price_recompute(self):
        if self.price_recompute:
            return self.with_context(warning="recompute")._get_warning_msg()

    @api.onchange("compute_price")
    def onchange_compute_price(self):
        self.base == "standard_price"
        self.is_price_pack == False

    @api.onchange("fixed_price_pack")
    def onchange_fixed_price(self):
        # if self.is_price_pack:
        self.fixed_price = self.fixed_price_pack / self.product_uom_pack.factor_inv
        self.price_pack = self.fixed_price_pack

    @api.onchange("product_id", "product_tmpl_id", "product_uom")
    def product_id_change_margin(self):
        product = self._get_product()

        if not self.pricelist_id or not product or not self.product_uom:
            return
        sale_order_line_obj = self.env["sale.order.line"]
        compute_data = sale_order_line_obj.with_context(item_id=self)
        self.product_cost = compute_data._compute_margin(
            self, product, self.product_uom
        )

    @api.depends(
        "date_update",
        "min_quantity",
        "product_cost",
        "percent_price",
        "fixed_price",
        "fixed_price_pack",
        "base_pricelist_id",
        "pricelist_id.tax_ids",
    )
    def _compute_amount(self):
        """
        Compute pricelist item amounts.
        """
        for item in self.filtered(
            lambda i: i.applied_on in ["0_product_variant", "1_product"]
        ):
            product = item._get_product()
            uom_factor = item.product_uom_pack.factor_inv or 1.0
            qty = uom_factor

            try:
                rule = self._origin
            except:
                rule = item
            pricelist = item.pricelist_id

            if not rule:
                rule = self.env["product.pricelist.item"].search(
                    [("id", "=", self._context.get("params")["id"])]
                )

            tax_ids = item.pricelist_id.tax_ids
            base_price, final_price = (
                item._get_price_unit(product, rule, tax_ids, pricelist) or 1.0
            )

            if item.compute_price == "fixed":
                final_price = item.fixed_price or 1.0

            price_pack = item.fixed_price_pack
            price_net_pack = tax_price_pack = 0.0

            if tax_ids:
                taxes = tax_ids.compute_all(
                    final_price,
                    item.pricelist_id.currency_id,
                    qty,
                    product=product,
                    partner=item.partner_ids,
                )
                tax_price_pack = sum(
                    t.get("amount", 0.0) for t in taxes.get("taxes", [])
                )

                price_pack = taxes["total_included"]
                price_net_pack = taxes["total_excluded"]

            item.update(
                {
                    "tax_price_unit": tax_price_pack / uom_factor,
                    "price_unit": final_price,
                    "price_net_unit": price_net_pack / uom_factor,
                    "tax_price_pack": tax_price_pack,
                    "price_pack": price_pack,
                    "price_net_pack": price_net_pack,
                    "product_cost_base": base_price,
                }
            )

    @api.depends("price_unit", "product_uom")
    def _product_margin(self):
        if not self.env.in_onchange:
            self.read(["price_unit", "product_cost", "min_quantity"])

        for item in self:
            product_cost_base = price_unit = price_net_unit = uom_factor = 1.0
            pricelist = item.pricelist_id
            product = item._get_product()

            if pricelist and product:
                taxes = pricelist.tax_ids
                uom_factor = item.product_uom_pack.factor_inv or 1.0
                price_unit = item.price_unit or 1.0
                price_net_unit = item.price_net_unit or 1.0
                product_cost_base = item.product_cost_base or 1.0

            margin_unit = price_unit - product_cost_base
            margin_net_unit = price_net_unit - product_cost_base
            margin_pack = margin_unit * uom_factor
            margin_net_pack = margin_net_unit * uom_factor
            margin_factor = margin_unit / price_unit
            margin_net_factor = margin_net_unit / price_net_unit
            item.margin_unit = margin_unit
            item.margin_net_unit = margin_net_unit
            item.margin_pack = margin_pack
            item.margin_net_pack = margin_net_pack
            item.margin_factor = margin_factor
            item.margin_net_factor = margin_net_factor

    @api.depends("product_id.standard_price", "product_tmpl_id.standard_price")
    def _product_cost(self):
        for item in self:
            product = item._get_product()

            if item.pricelist_id and product:
                sale_order_line_obj = self.env["sale.order.line"]
                compute_data = sale_order_line_obj.with_context(item_id=item)
                item.product_cost = compute_data._compute_margin(
                    item, product, item.product_uom
                )

    def _get_related_items(self, product, applied_on, pricelists):
        domain = [("base_pricelist_id", "=", pricelists.id)]
        domain_pricelist = [
            ("id", "!=", self.id),
            ("active_pricelist", "=", True),
            ("base_pricelist_id", "=", pricelists.id),
        ]
        domain_product = [("product_id", "=", product.id)]
        ritems = self.env["product.pricelist.item"]

        if product or pricelists:
            ritem_search = self.env["product.pricelist.item"]

            if applied_on == "0_product_variant":
                domain += domain_product

            ritem_search = self.env["product.pricelist.item"]
            pricelist_search = pricelists + self.base_pricelist_id
            count_ritems = len(self.env["product.pricelist"].search([]))

            while count_ritems >= 0:
                ritem_search = self.env["product.pricelist.item"].search(domain)
                ritems |= ritem_search

                for rsitem in ritem_search:
                    pricelist_search |= rsitem.pricelist_id + rsitem.base_pricelist_id

                pricelists |= pricelist_search
                del domain[:]
                domain_pricelist = [
                    ("id", "!=", self.id),
                    ("active_pricelist", "=", True),
                    ("base_pricelist_id", "in", ([plist.id for plist in pricelists])),
                ]
                domain = domain_pricelist
                
                if applied_on == "0_product_variant":
                    domain += domain_product

                ritem_search = self.env["product.pricelist.item"]
                pricelist_search = self.env["product.pricelist"]

                if not ritem_search:
                    count_ritems -= 1

        return ritems, pricelists

    # def recompute_items(self, items):
    #     """Wrapper for multi. Avoid recompute as it delays the pickings
    #        creation"""
    #     with self.env.norecompute():
    #         _logger.debug("_gri while for items >>>: %s", items)
    #         for ritem in items:
    #             _logger.debug("_gri while for items >>>: %s", ritem)
    #     self.recompute()

    def _recompute_items(self):
        self.ensure_one()
        # avoid recursion errors
        self.price_recompute = False
        # get related items by product
        ritem_ids, pricelist_ids = self._get_related_items(
            product=self.product_id,
            applied_on=self.applied_on,
            pricelists=self.pricelist_id,
        )
        date = fields.Datetime.now()

        # force recompute calling _write with onchange for product cost field
        if self.applied_on != "3_global":
            self._product_cost()

        ritem_ids = ritem_ids.filtered(lambda ritem: ritem.applied_on != "3_global")

        return date, pricelist_ids, ritem_ids

    @api.multi
    def _write(self, vals):
        res = super()._write(vals)
        date = False
        pricelist_ids = self.env["product.pricelist"]
        ritem_ids = self.env["product.pricelist.item"]

        # log update on base pricelist log
        for item in self.filtered(lambda i: i.price_recompute):
            # run recompute on related items
            # and get related pricelists and update date
            date, pricelist_ids, ritem_ids = item._recompute_items()
            item.update({"date_update": date})

        pricelist_ids.update({"date_update": date})
        ritem_ids.update({"date_update": date})

        return res
