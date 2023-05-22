from decimal import Decimal
from lxml import etree, objectify

from reportlab.lib import colors
# from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

########################################################################
class PDFfacturaElectronicaCompraVenta(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, xml_file, pdf_file, pagesize):
        """Constructor"""
        self.xml_file = xml_file
        self.pdf_file = pdf_file
        self.pagesize = pagesize
        
        self.xml_obj = self.getXMLObject()
        
    #----------------------------------------------------------------------
    def coord(self, x, y, unit=1):
        """
        # http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab
        Helper class to help position flowables in Canvas objects
        """
        x, y = x * unit, self.height -  y * unit
        return x, y  
        
    #----------------------------------------------------------------------
    def createPDF(self):
        """
        Create a PDF based on the XML data
        """
        # custom pagesizes
        ps_roll80mm = (80, 295)
        
        self.canvas = canvas.Canvas(self.pdf_file, pagesize=pagesize)
        width, self.height = pagesize
        styles = getSampleStyleSheet()
        xml = self.xml_obj

        title = "FACTURA CON DERECHO A CRÉDITO FISCAL"
        nitEmisor = xml.nitEmisor
        razonSocialEmisor = xml.razonSocialEmisor
        municipio = xml.municipio
        telefono = xml.telefono
        numeroFactura = xml.numeroFactura
        cuf = xml.cuf
        cufd = xml.cufd
        codigoSucursal = xml.codigoSucursal
        direccion = xml.direccion
        codigoPuntoVenta = xml.codigoPuntoVenta
        fechaEmision = xml.fechaEmision
        nombreRazonSocial = xml.nombreRazonSocial
        codigoTipoDocumentoIdentidad = xml.codigoTipoDocumentoIdentidad
        numeroDocumento = xml.numeroDocumento
        codigoCliente = xml.codigoCliente
        codigoMetodoPago = xml.codigoMetodoPago
        numeroTarjeta = xml.numeroTarjeta
        montoTotal = xml.montoTotal
        montoTotalSujetoIva = xml.montoTotalSujetoIva
        codigoMoneda = xml.codigoMoneda
        tipoCambio = xml.tipoCambio
        montoTotalMoneda = xml.montoTotalMoneda
        montoGiftCard = xml.montoGiftCard
        descuentoAdicional = xml.descuentoAdicional
        codigoExcepcion = xml.codigoExcepcion
        cafc = xml.caf
        leyenda = xml.leyenda
        usuario = xml.usuario
        codigoDocumentoSector = xml.codigoDocumentoSector

        subtt_detalle = "DETALLE"
        actividadEconomica = xml.actividadEconomica
        codigoProductoSin = xml.codigoProductoSin
        codigoProducto = xml.codigoProducto
        descripcion = xml.descripcion
        cantidad = xml.cantidad
        unidadMedida = xml.unidadMedida
        precioUnitario = xml.precioUnitario
        montoDescuento = xml.montoDescuento
        subTotal = xml.subTotal
        numeroSerie = xml.numeroSerie 
        numeroImei = xml.numeroSerie

        if codigoSucursal = 0:
            codigoSucursal = "Casa Matriz"

        cabecera_emisor = """ <font size="9">
        %s
        <br>
        <br>
        %s<br>
        %s<br>
        %s<br>
        %s<br>
        </font>
        """ % (title, razonSocialEmisor, codigoSucursal, codigoPuntoVenta, direccion, telefono, municipio)

        cabecera_emision = """ <font size="9">
        %s
        <br>
        <br>
        %s<br>
        %s<br>
        %s<br>
        %s<br>
        </font>
        """ % (nitEmisor, numeroFactura, cufd)

        cabecera_cliente = """ <font size="9">
        %s
        <br>
        <br>
        %s<br>
        %s<br>
        %s<br>
        %s<br>
        </font>
        """ % (nombreRazonSocial, numeroDocumento, codigoCliente, fechaEmision)

        address = """ <font size="9">
        SHIP TO:<br>
        <br>
        %s<br>
        %s<br>
        %s<br>
        %s<br>
        </font>
        """ % (xml.address1, xml.address2, xml.address3, xml.address4)
        p = Paragraph(address, styles["Normal"])
        p.wrapOn(self.canvas, width, self.height)
        p.drawOn(self.canvas, *self.coord(18, 40, mm))
        
        order_number = '<font size="14"><b>Order #%s </b></font>' % xml.order_number
        p = Paragraph(order_number, styles["Normal"])
        p.wrapOn(self.canvas, width, self.height)
        p.drawOn(self.canvas, *self.coord(18, 50, mm))
        
        data = []
        data.append(["Item ID", "Name", "Price", "Quantity", "Total"])
        grand_total = 0
        for item in xml.order_items.iterchildren():
            row = []
            row.append(item.id)
            row.append(item.name)
            row.append(item.price)
            row.append(item.quantity)
            total = Decimal(str(item.price)) * Decimal(str(item.quantity))
            row.append(str(total))
            grand_total += total
            data.append(row)
        data.append(["", "", "", "Grand Total:", grand_total])
        t = Table(data, 1.5 * inch)
        t.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black)
        ]))
        t.wrapOn(self.canvas, width, self.height)
        t.drawOn(self.canvas, *self.coord(18, 85, mm))
        
        txt = "Thank you for your business!"
        p = Paragraph(txt, styles["Normal"])
        p.wrapOn(self.canvas, width, self.height)
        p.drawOn(self.canvas, *self.coord(18, 95, mm))
        
    #----------------------------------------------------------------------
    def getXMLObject(self):
        """
        Open the XML document and return an lxml XML document
        """
        with open(self.xml_file) as f:
            xml = f.read()
        return objectify.fromstring(xml)
    
    #----------------------------------------------------------------------
    def savePDF(self):
        """
        Save the PDF to disk
        """
        self.canvas.save()
    
#----------------------------------------------------------------------
if __name__ == "__main__":
    xml = "order.xml"
    pdf = "letter.pdf"
    doc = PDFOrder(xml, pdf)
    doc.createPDF()
    doc.savePDF()