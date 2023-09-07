# -*- coding: utf-8 -*-

# import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.addons.poi_bol_siat.models.siat_utils import get_file

import xml.etree.ElementTree as ET

# _logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends(
        "invoice_line_ids.price_subtotal",
        "tax_line_ids.amount",
        "tax_line_ids.amount_rounding",
        "currency_id",
        "company_id",
        "date_invoice",
        "type",
    )
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()

        # Calculo final totales segun tipo especificos de impuestos SIN
        exe_sum = 0.0
        exe_sum = sum(
            line.amount for line in self.tax_line_ids if line.tax_id.type_bol == "exe"
        )
        self.amount_tax = self.amount_tax - exe_sum
        self.amount_tax_exempt = exe_sum
        self.amount_total = (
            self.amount_untaxed + self.amount_tax + self.amount_tax_exempt
        )

    nit = fields.Char(
        "NIT",
        size=22,
        help="NIT o CI del cliente.",
    )
    razon = fields.Char(
        "Razón Social",
        help="Nombre o Razón Social para la Factura.",
    )
    siat_state_display = fields.Selection(
        [
            ("offline", "No enviada"),
            ("error", "Error de envío"),
            ("online", "Enviada"),
            ("anulada", "Anulada"),
        ],
        string="Estado SIAT Display",
        readonly=True,
        compute="_get_siat_state",
    )
    amount_tax_exempt = fields.Monetary(
        string="Tax Exempt",
        readonly=True,
        store=True,
        compute="_compute_amount",
    )

    @api.one
    @api.depends("estado_fac")
    def _get_siat_state(self):
        if self.type in ("out_invoice", "out_refund"):
            self.siat_state_display = self.siat_state

    def _get_siat_partner_id(self):
        partner = False
        context_partner = self._context.get("partner")

        if context_partner:
            partner = context_partner
        elif self.partner_invoice_id:
            partner = self.partner_invoice_id
        elif self.partner_id:
            partner = self.partner_id

        return partner

    def _get_siat_tipo_id(self):
        partner = self.with_context(self._context)._get_siat_partner_id()
        siat_tipo_id = False

        # get siat_tipo_id from partner
        if partner:
            if partner.nit != 0:
                tipo_read = self.env["siat.tipo_id"].search(
                    [("code", "=", "5")], limit=1
                )
                siat_tipo_id = tipo_read and tipo_read[0] or False
            elif partner.ci != 0:
                tipo_read = self.env["siat.tipo_id"].search(
                    [("code", "=", "1")], limit=1
                )
                siat_tipo_id = tipo_read and tipo_read[0] or False

        return siat_tipo_id

    def _get_sin_data(self):
        context_vals = self._context.get("vals")
        vals = {}

        if context_vals:
            vals = context_vals

        partner = self.with_context(self._context)._get_siat_partner_id()
        method = self._context.get("method")
        siat_tipo_id = self.siat_tipo_id
        razon = False
        nit = 0
        ci_dept = False

        if partner:
            commercial_partner = partner.commercial_partner_id
            if method != "onchange_siat_tipo_id":
                siat_tipo_id = self.with_context(
                    partner=commercial_partner
                )._get_siat_tipo_id()
                razon = (
                    commercial_partner.razon_invoice
                    or commercial_partner.razon
                    or commercial_partner.name
                    or ""
                )
            if not siat_tipo_id:
                nit = 0
            elif siat_tipo_id.code == 5:
                if commercial_partner.nit != 0:
                    nit = commercial_partner.nit
            elif siat_tipo_id.code == 1:
                if commercial_partner.ci != 0:
                    nit = commercial_partner.ci
                    ci_dept = commercial_partner.ci_dept

            vals["siat_tipo_id"] = siat_tipo_id
            vals["razon"] = razon
            vals["nit"] = nit
            vals["ci_dept"] = ci_dept

        return vals

    @api.onchange("siat_tipo_id")
    def _onchange_siat_tipo_id(self):
        # get vals
        vals = self.with_context(method="onchange_siat_tipo_id")._get_sin_data()

        # update invoice with vals
        self.nit = vals["nit"]
        self.ci_dept = vals["ci_dept"]

        # run nit validations
        self._onchange_nit()

    @api.model
    def create(self, vals):
        partner = False
        out_invoice = False
        
        if "type" in vals:
            if "partner_invoice_id" in vals and vals["type"] in (
                "out_invoice",
                "out_refund",
            ):
                partner = vals["partner_invoice_id"]
                out_invoice = True
            elif "partner_id" in vals and vals["type"] in ("in_invoice", "in_refund"):
                partner = vals["partner_id"]
            if partner:
                partner = self.env["res.partner"].browse(partner)
                if out_invoice:
                    vals = self.with_context(partner=partner, vals=vals)._get_sin_data()
                    if vals["siat_tipo_id"]:
                        vals["siat_tipo_id"] = vals["siat_tipo_id"]["id"]
            
        ret = {}
        ret["result"] = super(AccountInvoice, self).create(vals)
        if partner and out_invoice:
            ret["validate_nit"] = ret["result"]._onchange_nit()

        return ret["result"]

    def _get_siat_onchange_vals(self):
        vals = self._get_sin_data()
        self.siat_tipo_id = vals["siat_tipo_id"]
        self.razon = vals["razon"]
        self.nit = vals["nit"]

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        if not self.partner_invoice_id:
            super(AccountInvoice, self)._onchange_partner_id()
            if self.siat_tipo_id:
                self._get_siat_onchange_vals()
            self._onchange_nit()
        else:
            self._onchange_partner_invoice_id()

    @api.onchange("partner_invoice_id", "company_id")
    def _onchange_partner_invoice_id(self):
        if not self.partner_invoice_id:
            self._onchange_partner_id()
        else:
            self._get_siat_onchange_vals()
            self._onchange_nit()

    @api.multi
    @api.depends("state")
    def _get_warehouse(self):
        res = super(AccountInvoice, self)._get_warehouse()
        for invoice in self:
            if invoice.cc_dos and invoice.type == "out_invoice":
                if invoice.cc_dos and not invoice.cc_dos.warehouse_id.journal_id:
                    raise ValidationError(
                        ("A journal must be set for the dosification branch.")
                    )
                else:
                    # set appropriate sale journal based on cc_dos.warehouse_id.journal_id
                    invoice.journal_id = invoice.cc_dos.journal_id
        return res

    @api.onchange("cc_dos")
    def _onchange_cc_dos(self):
        # get acc journal
        if self.cc_dos and self.type == "out_invoice":
            self._get_warehouse()

    @api.multi
    def get_taxes_values(self):
        tax_grouped = super().get_taxes_values()

        if self.invoice_line_ids.filtered(lambda l: l.is_tax_exempt_manual):
            tax_grouped = {}
            round_curr = self.currency_id.round

            for line in self.invoice_line_ids:
                # descuento, exento_manual for tax computation
                descuento = line.discount
                exento = line.tax_exempt
                price_unit = line.price_unit * (1 - (descuento or 0.0) / 100.0)
                taxes = line.invoice_line_tax_ids.with_context(
                    descuento=descuento, exento_manual=exento
                ).compute_all(
                    price_unit,
                    self.currency_id,
                    line.quantity,
                    line.product_id,
                    self.partner_id,
                )[
                    "taxes"
                ]
                for tax in taxes:
                    val = self._prepare_tax_line_vals(line, tax)
                    key = (
                        self.env["account.tax"].browse(tax["id"]).get_grouping_key(val)
                    )
                    if key not in tax_grouped:
                        tax_grouped[key] = val
                        tax_grouped[key]["base"] = round_curr(val["base"])
                    else:
                        tax_grouped[key]["amount"] += val["amount"]
                        tax_grouped[key]["base"] += round_curr(val["base"])

        return tax_grouped

    def _check_siat_uoms(self):
        res = []
        invoice_lines = self._context.get("invoice_lines")
        uoms = [line.uom_id for line in invoice_lines]

        for uom in uoms:
            if not uom.siat_unidad_medida_id:
                raise ValidationError(
                    _(
                        "La UdM %s no tiene una UdM SIAT establecida. "
                        "Por favor establezca una e intente nuevamente."
                    )
                    % (uom.name)
                )
            res.append(uom.siat_unidad_medida_id)

        return res

    def mod_xml_siat(self):
        xml = self._context.get("result")
        tree = ET.ElementTree(ET.fromstring(str(xml, encoding="utf-8")))
        root = tree.getroot()
        xml_uoms = [uom for uom in root.iter("unidadMedida")]
        siat_uoms = self._context.get("siat_uoms")

        # _logger.debug("mxs siat_uoms >>>: %s", siat_uoms)
        # _logger.debug("mxs uom >>>: %s", [uom.code for uom in siat_uoms])

        # iterate through xml_uoms and replace with siat_uoms
        for i in range(len(xml_uoms)):
            xml_uoms[i].text = str(siat_uoms[i].code)

        return get_file(ET.tostring(root, encoding="utf8").decode("utf8"))

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            res = super(AccountInvoice, invoice).action_invoice_open()

            if invoice.cc_dos:
                # check for valid nit
                if invoice.nit == "0":
                    raise ValidationError(
                        _("%s no puede ser 0. " "Por favor ingrese un numero valido.")
                        % (invoice.siat_tipo_id.name)
                    )

                invoice_lines = invoice.invoice_line_ids

                # validate siat_uoms set on uom_id
                invoice.with_context(invoice_lines=invoice_lines)._check_siat_uoms()

        return res

    # @api.multi
    def get_xml_siat(self):
        for invoice in self:
            res = super(AccountInvoice, invoice).get_xml_siat()

            invoice_lines = invoice.invoice_line_ids

            # validate siat_uoms set on uom_id
            siat_uoms = invoice.with_context(
                invoice_lines=invoice_lines
            )._check_siat_uoms()

            if siat_uoms:
                # mod xml if uom_id/product_id siat_uoms don't match
                if any(
                    line.uom_id.siat_unidad_medida_id
                    != line.product_id.siat_unidad_medida_id
                    for line in invoice_lines
                ):
                    result = invoice.with_context(
                        result=res, siat_uoms=siat_uoms
                    ).mod_xml_siat()
                    res = result

        return res

    @api.one
    def siat_recepcionDocumentoAjuste(self):
        self.ensure_one()
        res = super().siat_recepcionDocumentoAjuste()

        inv_lines = self.invoice_line_ids
        if [
            line.uom_id.siat_unidad_medida_id != line.product_id.siat_unidad_medida_id
            for line in inv_lines
        ]:
            result = self.with_context(result=res).mod_xml_siat()
            res = result

        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    tax_exempt = fields.Monetary(string="Tax Exempt")
    is_tax_exempt_manual = fields.Boolean(
        string="Manual tax exempt",
        default=False,
        readonly=True,
        store=True,
        help="Manually set the exempted tax.",
    )

    @api.onchange("invoice_line_tax_ids")
    def onchange_invoice_line_tax_ids(self):
        is_tax_exempt_manual = any(
            tax.is_exento_manual for tax in self.invoice_line_tax_ids
        )
        self.is_tax_exempt_manual = is_tax_exempt_manual
        if len(self.invoice_line_tax_ids) > 1 and is_tax_exempt_manual:
            raise ValidationError(
                (
                    "Only one tax can be selected if one of them has manual tax exemption: [%s] ."
                    % self.invoice_line_tax_ids.filtered(
                        lambda t: t.is_exento_manual
                    ).name
                )
            )
        self.tax_exempt = 0.0

    def _get_taxes_vals(self):
        exento = self.tax_exempt
        descuento = self.discount
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (descuento or 0.0) / 100.0)
        taxes = (
            self._context.get("taxes")
            .with_context(descuento=descuento, exento_manual=exento)
            .compute_all(
                price,
                currency,
                self.quantity,
                product=self.product_id,
                partner=self.invoice_id.partner_id,
            )
        )
        obj_tax_ids = self._context.get("taxes") | self._context.get("taxes").mapped(
            "children_tax_ids"
        )
        for tax in taxes["taxes"]:
            tax_id = obj_tax_ids.filtered(lambda t: t.id == tax["id"])
            tax["type_bol"] = tax_id.type_bol or False
        return taxes

    def _get_tax_exempt_amount(self):
        if not self.is_tax_exempt_manual:
            taxes = self._context.get("tax_vals")
            self.tax_exempt = sum(
                tax["amount"] for tax in taxes["taxes"] if tax["type_bol"] == "exe"
            )

    @api.one
    @api.depends(
        "price_unit",
        "discount",
        "invoice_line_tax_ids",
        "quantity",
        "product_id",
        "invoice_id.partner_id",
        "invoice_id.currency_id",
        "invoice_id.company_id",
        "invoice_id.date_invoice",
        "invoice_id.date",
    )
    def _compute_price(self):
        res = super()._compute_price()

        taxes = self.invoice_line_tax_ids
        taxes_exe = any(t.type_bol == "exe" for t in taxes) or any(
            ch.type_bol == "exe" for t in taxes for ch in t.children_tax_ids
        )
        if taxes_exe:
            taxes = self.with_context(taxes=taxes)._get_taxes_vals()
            self.with_context(tax_vals=taxes)._get_tax_exempt_amount()
            self.price_subtotal = price_subtotal_signed = (
                taxes["total_excluded"] if taxes else self.quantity * price
            )
            self.price_total = taxes["total_included"] if taxes else self.price_subtotal
            if (
                self.invoice_id.currency_id
                and self.invoice_id.currency_id
                != self.invoice_id.company_id.currency_id
            ):
                price_subtotal_signed = self.invoice_id.currency_id.with_context(
                    date=self.invoice_id._get_currency_rate_date()
                ).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
            sign = self.invoice_id.type in ["in_refund", "out_refund"] and -1 or 1
            self.price_subtotal_signed = price_subtotal_signed * sign
        else:
            return res
