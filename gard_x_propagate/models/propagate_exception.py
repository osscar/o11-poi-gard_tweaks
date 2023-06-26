# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropagateException(models.Model):
    _name = "propagate.exception"

    def _exception_check(self, params):
        # context parameters for conditional statement
        # check exception
        exc_msg = params["exc_msg"] + exc_states["name"]
        if params["is_exc"]:
            raise ValidationError(("%s") % exc_msg)

        return True
