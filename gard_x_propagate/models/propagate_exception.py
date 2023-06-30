# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# import logging

from odoo import models, _
from odoo.exceptions import ValidationError

# _logger = logging.getLogger(__name__)


class PropagateException(models.Model):
    _name = "propagate.exception"

    def _get_exception_msg(self, vals):
        # compose exception message
        model = self.env[vals["model"]]
        field = vals["field"]
        message = vals["msg"]

        # state field message
        if field == "state":
            state_names = [
                rs[1]
                for rs in model._fields.get(field).selection
                if rs[0] in vals["field_vals"]
            ]
            message += ", ".join(state_names) + "."

        return message

    def _exception_check(self, vals):
        # check exceptions
        exc_vals = vals["exc_vals"]
        is_exc = False
        
        # state field exceptions
        if exc_vals["field"] == "state":
            is_exc = any(
                ev not in exc_vals["field_vals"] for ev in exc_vals["field_rec_vals"]
            )
        
        if is_exc:
            # get exception message
            exc_msg = self._get_exception_msg(exc_vals)
            raise ValidationError(("%s") % exc_msg)

        return True
