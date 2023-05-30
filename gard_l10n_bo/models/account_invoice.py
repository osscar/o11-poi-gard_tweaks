# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.addons.poi_bol_siat.models.siat_utils import get_file

import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    nit = fields.Char(
        "NIT",
        size=22,
        help="NIT o CI del cliente.",
    )
    razon = fields.Char(
        "Razón Social",
        help="Nombre o Razón Social para la Factura.",
    )

    def _get_siat_partner_id(self):
        partner = False
        context_partner = self._context.get("partner")

        if context_partner:
            partner = context_partner
        elif self.partner_invoice_id:
            partner = self.partner_invoice_id
        elif self.partner_id:
            partner = self.partner_id
        
        _logger.debug("_gspid partner >>>: %s", partner)
        _logger.debug("_gspid context_partner >>>: %s", context_partner)
        
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
            if siat_tipo_id.code == 5:
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
        
        #update invoice with vals
        self.nit = vals["nit"]
        self.ci_dept = vals["ci_dept"]

        # run nit validations
        self._onchange_nit()

    @api.model
    def create(self, vals):
        _logger.debug("create vals >>>: %s", vals)
        if "type" in vals:
            partner = False

            if "partner_invoice_id" in vals and vals["type"] in (
                "out_invoice",
                "out_refund",
            ):
                partner = vals["partner_invoice_id"]
            elif "partner_id" in vals and vals["type"] in ("in_invoice", "in_refund"):
                partner = vals["partner_id"]

            if partner:
                partner = self.env["res.partner"].browse(partner)
                vals = self.with_context(partner=partner, vals=vals)._get_sin_data()
                vals["siat_tipo_id"] = vals["siat_tipo_id"]["id"]

        ret = {}
        ret["result"] = super(AccountInvoice, self).create(vals)
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

        _logger.debug("mxs siat_uoms >>>: %s", siat_uoms)
        _logger.debug("mxs uom >>>: %s", [uom.code for uom in siat_uoms])

        # iterate through xml_uoms and replace with siat_uoms
        for i in range(len(xml_uoms)):
            xml_uoms[i].text = str(siat_uoms[i].code)

        return get_file(ET.tostring(root, encoding="utf8").decode("utf8"))

    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            res = super(AccountInvoice, invoice).action_invoice_open()

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
