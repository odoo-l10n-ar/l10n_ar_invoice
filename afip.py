# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2012 OpenERP - Team de Localización Argentina.
# https://launchpad.net/~openerp-l10n-ar-localization
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv

class afip_responsability(osv.osv):
    _name='afip.responsability'
    _description='VAT Responsability'
    _columns={
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
    }
    _sql_constraints = [('name','unique(name)', 'Not repeat name!'),
                        ('code','unique(code)', 'Not repeat code!')]
afip_responsability()

class afip_responsability_class(osv.osv):
    _name='afip.responsability_class'
    _description='Responsability Interaction'
    _columns={
        'name': fields.char('Name', size=64),
        'emisor_id': fields.many2one('afip.responsability', 'Emisor', required=True),
        'receptor_id': fields.many2one('afip.responsability', 'Receptor', required=True),
        'document_class': fields.char('Journal Class', size=3, required=True),
    }
    _sql_constraints = [('main_constraints','unique(emisor_id, receptor_id, document_class)', 'Not configuration!'),
                        ('name','unique(name)', 'Not repeat name!')]
afip_responsability_class()

class afip_journal_class(osv.osv):
    _name='afip.journal_class'
    _description='AFIP Journal types'
    _columns={
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
        'document_class': fields.char('Class', size=3, required=True),
        'type': fields.selection([('sale', 'Sale'),('sale_refund','Sale Refund'), ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Cheques'), ('general', 'General'), ('situation', 'Opening/Closing Situation')], 'Type', size=32, required=True,
                                 help="Select 'Sale' for Sale journal to be used at the time of making invoice."\
                                 " Select 'Purchase' for Purchase Journal to be used at the time of approving purchase order."\
                                 " Select 'Cash' to be used at the time of making payment."\
                                 " Select 'General' for miscellaneous operations."\
                                 " Select 'Opening/Closing Situation' to be used at the time of new fiscal year creation or end of year entries generation."),
        'afip_code': fields.integer('AFIP Code'),
    }
    _sql_constraints = [('name','unique(name)', 'Not repeat name!')]
afip_journal_class()

class afip_document_type(osv.osv):
    _name = 'afip.document_type'
    _description='AFIP document types'
    _columns = {
        'name': fields.char('Name', size=120),
        'code': fields.char('Code', size=16),
        'afip_code': fields.integer('AFIP Code'),
    }
afip_document_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
