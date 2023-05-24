# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.addons.poi_bol_siat.models.siat_utils import get_file

import xml.etree.ElementTree as ET
from io import StringIO, BytesIO

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

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
        siat_uoms = self._context.get("siat_uoms")
        
        _logger.debug("_csu siat_uoms >>>>: %s", siat_uoms)
        _logger.debug("_csu siat_uom >>>>: %s", [siat_uom for siat_uom in siat_uoms])
        
        if any(
            siat_uom == 0
            for siat_uom in siat_uoms
        ):
            raise ValidationError(
                _(
                    "Una UdM en las lineas de factura, no tiene una UdM SIAT establecida. "
                    "Por favor establezca una e intente nuevamente."
                )
            )
        else:
            return True
        
    def mod_xml_siat(self):
        xml = self._context.get("result")
        tree = ET.ElementTree(ET.fromstring(str(xml, encoding="utf-8")))
        root = tree.getroot()
        xml_uoms = [uom for uom in root.iter("unidadMedida")]
        siat_uoms = self._context.get("siat_uoms")
        
        _logger.debug("_csu siat_uom >>>>: %s", [siat_uom for siat_uom in siat_uoms])

        # iterate through xml_uoms and replace with siat_uoms
        for i in range(len(xml_uoms)):
            xml_uoms[i].text = str(siat_uoms[i])

        return get_file(ET.tostring(root, encoding="utf8").decode("utf8"))

    @api.multi
    def action_invoice_open(self):
        for inv in self:
            res = super(AccountInvoice, inv).action_invoice_open()

            inv_lines = inv.invoice_line_ids
            siat_uoms = [line.uom_id.siat_unidad_medida_id.code for line in inv_lines]

            get_xml = inv.get_xml_siat()

            _logger.debug("_csu siat_uom >>>>: %s", [siat_uom for siat_uom in siat_uoms])

            # validate siat_uoms set on uom_id
            [inv.with_context(inv_lines=inv_lines, siat_uoms=siat_uoms)._check_siat_uoms() for inv in self]

            # mod xml if uom_id/product_id siat_uoms don't match
            if [
                line.uom_id.siat_unidad_medida_id != line.product_id.siat_unidad_medida_id
                for line in inv_lines
            ]:
                result = inv.with_context(result=get_xml, inv_lines=inv_lines, siat_uoms=siat_uoms).mod_xml_siat()
                res = result

        return res

    # def get_xml_siat(self):
    #     self.ensure_one()
    #     res = super().get_xml_siat()

    #     inv_lines = self.invoice_line_ids
    #     siat_uoms = [line.uom_id.siat_unidad_medida_id.code for line in inv_lines]
        
    #     # mod xml if uom_id/product_id siat_uoms don't match
    #     if [
    #         line.uom_id.siat_unidad_medida_id != line.product_id.siat_unidad_medida_id
    #         for line in inv_lines
    #     ]:
    #         result = self.with_context(result=res, inv_lines=inv_lines, siat_uoms=siat_uoms).mod_xml_siat()
    #         res = result

    #     return res

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
