# -*- encoding: utf-8 -*-
import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    vehicle_id = fields.Many2one(
        'fleet.vehicle', 
        'Vehicle', 
        readonly="True", 
        states={
            'draft': [('readonly', False)],
            'assigned': [('readonly', False)]
            }, 
        help='Delivery vehicle.')
    odometer_start = fields.Float(string='Start Odometer', readonly=True)
    odometer_end = fields.Float(string='End Odometer', readonly="True", states={
            'draft': [('readonly', False)],
            'assigned': [('readonly', False)]
        },)
    driver_id = fields.Many2one('res.users', 'Driver', help='Delivery driver.', required=True, default=lambda self: self.env.user, readonly="True", states={
            'draft': [('readonly', False)],
            'assigned': [('readonly', False)]
        })
    assistant_ids = fields.Many2many('res.users', string='Assistants', readonly="True", states={
            'draft': [('readonly', False)],
            'assigned': [('readonly', False)]
        }, help='Delivery assitants.')
    
    @api.onchange("vehicle_id")
    def onchange_vehicle_id(self):
        odometer_start = 0.0
        if self.vehicle_id:
            odometer_start = self.vehicle_id.odometer
        self["odometer_start"] = odometer_start

    def check_vehicle_data(self):
        if not self.vehicle_id:
            raise ValidationError(_("Please select a vehicle."))
        if self.odometer_end <= (self.vehicle_id.odometer or 0):
            raise ValidationError(_("Ending odometer value cannot be the same as start value or 0."))
        
    @api.onchange("odometer_end")
    def onchange_odometer_end(self):
        if self.vehicle_id:
            self.check_vehicle_data()
               
    @api.multi
    def action_transfer(self):
        super().action_transfer()
        _logger.debug('a_t self >>> %s', self)
        self.check_vehicle_data()
        if self.state == "done":
            self.vehicle_id.write({
                "driver_id": self.driver_id.partner_id.id,
                "odometer": self.odometer_end
            })