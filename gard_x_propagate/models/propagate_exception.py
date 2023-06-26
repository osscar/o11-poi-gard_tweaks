# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PropagateException(models.Model):
    _name = "propagate.exception"

    def _exception_check(self):
        # context parameters for conditional statement
        ctx = self._context.get("ctx")
        # check exception

        _logger.debug("_ec ctx >>>: %s", ctx)
        _logger.debug("_ec ctx[fields] >>>: %s", ctx["exc_field"])
        _logger.debug("_ec ctx[exc_vals] >>>: %s", ctx["exc_vals"])

        if ctx["exc_field"] in ctx["exc_vals"]:
            raise ValidationError(("%s") % ctx["exc_msg"])

        return True
