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

class afip_journal_template(osv.osv):
    _name = 'afip.journal_template'
    _columns = {
        'name': fields.char('Name', size=120),
        'code': fields.integer('Code'),
    }
afip_journal_template()

class afip_document_class(osv.osv):
    _name='afip.document_class'
    _description='Document class'
    _columns={
        'name': fields.char('Name', size=64, required=True),
        'description': fields.text('Description'),
        'responsability_relation_ids': fields.one2many('afip.responsability_relation','document_class_id', 'Reponsability relations'),
        'journal_class_ids': fields.one2many('afip.journal_class', 'document_class_id', 'Journal classes'),
    }
    _sql_constraints = [('name','unique(name)', 'Not repeat name!'),]
afip_document_class()

class afip_responsability(osv.osv):
    _name='afip.responsability'
    _description='VAT Responsability'
    _columns={
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
        'active': fields.boolean('Active'),
        'issuer_relation_ids': fields.one2many('afip.responsability_relation', 'issuer_id', 'Issuer relation'),
        'receptor_relation_ids': fields.one2many('afip.responsability_relation', 'receptor_id', 'Receptor relation'),
    }
    _sql_constraints = [('name','unique(name)', 'Not repeat name!'),
                        ('code','unique(code)', 'Not repeat code!')]
afip_responsability()

class afip_responsability_relation(osv.osv):
    _name='afip.responsability_relation'
    _description='Responsability Interaction'
    _columns={
        'name': fields.char('Name', size=64),
        'issuer_id': fields.many2one('afip.responsability', 'Issuer', required=True),
        'receptor_id': fields.many2one('afip.responsability', 'Receptor', required=True),
        'document_class_id': fields.many2one('afip.document_class', 'Document class', required=True),
        'active': fields.boolean('Active'),
    }
    _sql_constraints = [('main_constraints','unique(issuer_id, receptor_id, document_class_id)', 'Not configuration!'),
                        ('name','unique(name)', 'Not repeat name!')]
afip_responsability_relation()

class afip_journal_class(osv.osv):
    _name='afip.journal_class'
    _description='AFIP Journal types'
    _columns={
        'name': fields.char('Name', size=64, required=True),
        'code': fields.char('Code', size=8, required=True),
        'document_class_id': fields.many2one('afip.document_class', 'Document Class'),
        'type': fields.selection([('sale', 'Sale'),('sale_refund','Sale Refund'), ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Cheques'), ('general', 'General'), ('situation', 'Opening/Closing Situation')], 'Type', size=32, required=True,
                                 help="Select 'Sale' for Sale journal to be used at the time of making invoice."\
                                 " Select 'Purchase' for Purchase Journal to be used at the time of approving purchase order."\
                                 " Select 'Cash' to be used at the time of making payment."\
                                 " Select 'General' for miscellaneous operations."\
                                 " Select 'Opening/Closing Situation' to be used at the time of new fiscal year creation or end of year entries generation."),
        'afip_code': fields.integer('AFIP Code'),
        'journal_ids': fields.one2many('account.journal', 'journal_class_id', 'Journals'),
        'active': fields.boolean('Active'),
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
        'active': fields.boolean('Active'),
    }
afip_document_type()

class afip_concept_type(osv.osv):
    _name = 'afip.concept_type'
    _description='AFIP concept types'
    _columns = {
        'name': fields.char('Name', size=120),
        'code': fields.char('Code', size=16),
        'afip_code': fields.integer('AFIP Code'),
        'active': fields.boolean('Active'),
    }
afip_concept_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
