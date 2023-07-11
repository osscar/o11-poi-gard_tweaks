# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError

from odoo.addons.poi_bol_siat.models.siat_ws import SiatService

_logger = logging.getLogger(__name__)


class SiatCancelInvoice(models.TransientModel):
    """
    Siat invoice cancel wizard.
    """

    _name = "siat.cancel.invoice"
    _description = "Send cancel request to the SIAT service."

    # invoice_ids = fields.Many2many(
    #     'account.invoice', string='Select Invoices',
    # )
    wizard_line = fields.One2many(
        "siat.cancel.invoice.line",
        "wizard_id",
        string="Wizard Lines",
    )

    def siat_cancel_invoice(self, invoice):
        # self.ensure_one()
        # invoice_obj = self.env["account_invoice"]
        # if invoice.type == "manual":

        base_dosif = invoice.dosif_id
        sector = base_dosif.siat_sector_id.code
        caso_siat_fac = ""

        if sector == 24:
            method = "anulacionDocumentoAjuste"
            caso_siat_fac = "siat.notas_cd.electronica"
            tipo = 3
        elif sector == 1:
            method = "anulacionFactura"
            caso_siat_fac = "siat.facturas"
            tipo = base_dosif.siat_sector_id.tipo
        else:
            method = "anulacionFactura"
            tipo = base_dosif.siat_sector_id.tipo
            if base_dosif.mode == "1":
                caso_siat_fac = "siat.facturas.electronica"
            elif base_dosif.mode == "2":
                caso_siat_fac = "siat.facturas.computarizada"

        ambiente = self.env["res.config.settings"].siat_cod_ambiente()
        SolicitudServicioAnulacionFactura = {
            "codigoAmbiente": ambiente,
            "codigoDocumentoSector": sector,
            "codigoEmision": 1,  # Online desde esta función
            "codigoModalidad": int(base_dosif.mode),
            "codigoPuntoVenta": base_dosif.pdv,
            "codigoSistema": self.env["res.config.settings"].siat_cod_sistema(),
            "codigoSucursal": base_dosif.sucursal,
            "cufd": base_dosif.cufd,
            "cuis": base_dosif.cuis,
            "nit": invoice.company_id.nit,
            "tipoFacturaDocumento": tipo,
            "codigoMotivo": invoice.motivo_code,
            "cuf": invoice.cuf,
        }

        # invoice_dup = self.check_invoice_duplicate(SolicitudServicioAnulacionFactura)
        # if invoices_dup:
        #     raise ValidationError(
        #         "[SIAT] %s \n\n Contacte al Responsable de Contabilidad para generar un CUFD vigente."
        #         % (siat_descripcion,)
        #     )

        # Llamar el servicio web del SIAT
        response = SiatService(caso_siat_fac, self.env).service(
            method, SolicitudServicioAnulacionFactura
        )

        codigoEstado = response["codigoEstado"]
        transaccion = response["transaccion"]
        codigoRecepcion = response["codigoRecepcion"]
        codigoDescripcion = response["codigoDescripcion"]
        mensajesList = response["mensajesList"]
        siat_codigo = mensajesList and mensajesList[0]["codigo"] or False
        siat_descripcion = mensajesList and mensajesList[0]["descripcion"] or ""

        _logger.debug("sci transaccion >>>: %s", transaccion)
        _logger.debug("sci transaccion >>>: %s", response)

        # voucher_obj = self.env["siat_cancel_voucher"]
        if not transaccion:
            if siat_codigo == 123:
                raise UserError(
                    "[SIAT] %s \n\n Contacte al Responsable de Contabilidad para generar un CUFD vigente."
                    % (siat_descripcion,)
                )
            else:
                raise UserError(
                    "[SIAT] No se ha podido anular la factura en el SIAT: \n %s"
                    % (str(mensajesList),)
                )
        # else:
        #     voucher_vals = {"siat_state": "cancel",
        #                     "nit": inv.nit,
        #                     "base_dosif": inv.cc_nro,
        #                     "cc_nro": inv.cc_nro,
        #                     "date_invoice": inv.date,
        #                     "cufd": inv.cufd,}
        #     voucher_obj.create({'siat_state': 'anulada'})

    # def button_create_wizard_line(self):
    #     for product in self.product_ids:
    #         line_vals = {
    #             "wizard_id": self.id,
    #         }
    #         self.wizard_line.create(line_vals)
    #     return {
    #         "type": "set_scrollTop",
    #     }

    @api.one
    def button_siat_cancel_invoices(self):
        for inv in self.wizard_line:
            self.siat_cancel_invoice(inv)

        return {
            "type": "set_scrollTop",
        }

    # def button_invoice_ids_clear(self):
    #     self.invoice_ids = False
    #     return {
    #         "type": "set_scrollTop",
    #     }

    def button_wizard_line_unlink(self):
        for line in self.wizard_line:
            line.unlink()
        return {
            "type": "set_scrollTop",
        }


class SiatCancelInvoiceLine(models.TransientModel):
    """
    Wizard line.
    """

    _name = "siat.cancel.invoice.line"
    _description = "Wizard lines."

    company_id = fields.Many2one('res.company', string='Company')
    emision_code = fields.Char(string="Emission Code", required=True, help=".")
    dosif_id = fields.Many2one('poi_bol_base.cc_dosif', string='Dosificación')
    cc_nro = fields.Char(string="# Factura", required=True, help=".")
    nit = fields.Char(string="NIT", required=True, help=".")
    motivo_code = fields.Char(string="Codigo Motivo", required=True, help=".")
    cuf = fields.Char(string="CUF", required=True, help=".")
    wizard_id = fields.Many2one(
        "siat.cancel.invoice",
        string="Wizard ID",
        ondelete="cascade",
    )
