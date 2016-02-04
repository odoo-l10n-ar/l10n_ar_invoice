# -*- coding: utf-8 -*-
from openerp import fields, models

class afip_country(models.Model):
    _inherit = 'res.country'

    afip_destination_ids=fields.Many2many('afip.destination',
                                          string='AFIP destinations')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
